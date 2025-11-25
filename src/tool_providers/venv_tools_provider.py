import os
import subprocess
import sys
import venv
import tempfile
from .tool_provider_base import ToolProviderBase

class VenvToolsProvider(ToolProviderBase):
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.venv_path = ".venv"
        self._create_venv()
    
    def run_script(self, script_code: str) -> str:
        """Execute a Python snippet in the repo's virtual environment.

        Use this tool to validate that your generated example script
        actually runs against the cloned repository.

        The code is executed as a temporary ``.py`` file located at the
        repository root using the Python interpreter from ``.venv``.

        Args:
            script_code: Complete Python source code for the script you
                want to run. It should be self-contained and import
                from the repository using relative or absolute imports
                as appropriate.

        Returns:
            ``stdout`` from the script if it exits successfully.
            If the script fails, a string starting with ``"Error:"``
            followed by the captured error output.
        """

        venv_full_path = os.path.join(self.base_dir, self.venv_path)
        
        # Determine the path to the python executable in the new venv
        if sys.platform == "win32":
            python_executable = os.path.join(venv_full_path, "Scripts", "python.exe")
        else:
            python_executable = os.path.join(venv_full_path, "bin", "python")
        
        # Write the script code to a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", dir=self.base_dir, delete=False, encoding="utf-8") as temp_script:
            script_file = temp_script.name
            
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script_code)
        
        # Run the script using the venv's python
        result = subprocess.run(
            [python_executable, script_file],
            capture_output=True,
            text=True,
            cwd=self.base_dir,
            check=False
        )
        
        # Clean up the temporary script file
        os.remove(script_file)
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        return result.stdout

    def add_missing_package(self, package_name: str) -> str:
        """Install a missing package into the repo virtual environment.

        Call this when ``run_script`` fails because a third-party
        dependency is not installed. This allows you to iteratively fix
        import errors while refining the example script.

        Args:
            package_name: The name of the package to install, exactly as
                you would pass it to ``pip install`` (for example
                ``"pandas"`` or ``"numpy>=1.26"``).

        Returns:
            A success message if installation appears to have completed,
            or a string starting with ``"Error installing package:"``
            if ``pip`` reported a failure.
        """
        venv_full_path = os.path.join(self.base_dir, self.venv_path)
        
        # Determine the path to the pip executable in the new venv
        if sys.platform == "win32":
            pip_executable = os.path.join(venv_full_path, "Scripts", "pip.exe")
        else:
            pip_executable = os.path.join(venv_full_path, "bin", "pip")
        
        # Install the package
        result = subprocess.run(
            [pip_executable, "install", package_name],
            capture_output=True,
            text=True,
            cwd=self.base_dir,
            check=False
        )
        
        if result.returncode != 0:
            return f"Error installing package: {result.stderr}"
        
        return f"Package '{package_name}' installed successfully."

    def _create_venv(self) -> str:
        venv_full_path = os.path.join(self.base_dir, self.venv_path)
        
        # Create the virtual environment
        venv.create(venv_full_path, with_pip=True)
        
        # Determine the path to the pip executable in the new venv
        if sys.platform == "win32":
            pip_executable = os.path.join(venv_full_path, "Scripts", "pip.exe")
        else:
            pip_executable = os.path.join(venv_full_path, "bin", "pip")
            
        requirements_file = os.path.join(self.base_dir, "requirements.txt")
        pyproject_file = os.path.join(self.base_dir, "pyproject.toml")
        uv_lock_file = os.path.join(self.base_dir, "uv.lock")
        
        # Generate requirements.txt in all cases
        if os.path.exists(uv_lock_file):
            # Generate requirements.txt from uv.lock
            subprocess.run(
                ["uv", "export", "--format", "requirements-txt", "--output-file", "requirements.txt"], 
                cwd=self.base_dir, 
                capture_output=True,
                check=False
            )
        elif os.path.exists(pyproject_file):
            # Generate requirements.txt from pyproject.toml using uv
            subprocess.run(
                ["uv", "pip", "compile", "pyproject.toml", "-o", "requirements.txt"],
                cwd=self.base_dir,
                capture_output=True,
                check=False
            )
        else:
            # Generate requirements.txt using pipreqs
            subprocess.run(
                [sys.executable, "-m", "pipreqs.pipreqs", ".", "--force", "--ignore", self.venv_path], 
                cwd=self.base_dir, 
                capture_output=True,
                check=False
            )

        # Handle existing requirements or pyproject files
        if os.path.exists(requirements_file):
            self._install_requirements_safely(pip_executable, requirements_file)
        elif os.path.exists(pyproject_file):
            # For pyproject.toml, we attempt to install via pip install .
            # We remove check=True so the venv creation doesn't crash entirely if it fails
            subprocess.run(
                [pip_executable, "install", "."], 
                cwd=self.base_dir,
                capture_output=True,
                check=False 
            )
            
        return venv_full_path

    def _install_requirements_safely(self, pip_executable: str, requirements_file: str):
        """
        Reads requirements.txt and installs packages one by one.
        Failures are ignored so valid packages are still installed.
        """
        try:
            with open(requirements_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in lines:
                package = line.strip()
                # Skip comments and empty lines
                if not package or package.startswith("#"):
                    continue
                
                # Attempt to install the individual package
                # check=False ensures the script doesn't stop on failure
                subprocess.run(
                    [pip_executable, "install", package],
                    cwd=self.base_dir,
                    check=False,
                    capture_output=True # Suppress output to keep console clean, or remove to see errors
                )
        except Exception as e:
            # Catch file reading errors or other unforeseen issues
            print(f"Warning: Could not process requirements file fully: {e}")