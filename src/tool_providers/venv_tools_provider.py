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
        """Runs a python script at the root directory and returns the output if it runs successfully, and the 
        error message otherwise."""

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
            cwd=self.base_dir
        )
        
        # Clean up the temporary script file
        os.remove(script_file)
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        return result.stdout

    def add_missing_package(self, package_name: str) -> str:
        """Installs a missing package into the virtual environment."""
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
            cwd=self.base_dir
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
        uv_lock_file = os.path.join(self.base_dir, "uv.lock")
        
        # If requirements.txt doesn't exist, try to generate it
        if not os.path.exists(requirements_file):
            if os.path.exists(uv_lock_file):
                # Generate requirements.txt from uv.lock
                subprocess.run(
                    ["uv", "export", "--format", "requirements-txt", "--output-file", "requirements.txt"], 
                    cwd=self.base_dir, 
                    check=True
                )
            else:
                # Generate requirements.txt using pipreqs
                subprocess.run(
                    [sys.executable, "-m", "pipreqs.pipreqs", ".", "--force", "--ignore", self.venv_path], 
                    cwd=self.base_dir, 
                    check=True
                )
        
        # Install dependencies if requirements.txt exists
        if os.path.exists(requirements_file):
            subprocess.run(
                [pip_executable, "install", "-r", "requirements.txt"], 
                cwd=self.base_dir, 
                check=True
            )
            
        return venv_full_path