import os
from .tool_provider_base import ToolProviderBase

from src.core.Logger import Logger

class FileSystemToolsProvider(ToolProviderBase):

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def list_directory(self, path: str = "") -> str:
        """List project files and folders to discover entry points.

        This tool is intended to help an agent explore a cloned
        repository when designing an example usage script.

        - It lists files and directories under ``path`` (relative to the
            repository root) up to a depth of 2.
        - Directories are prefixed with ``[DIR]``.
        - Files are prefixed with ``[FILE]`` and show their line count
            in parentheses.
        - Use this output to decide which modules or scripts to inspect
            next with ``read_file_snippet`` or search tools.

        Args:
                path: Directory path relative to the repository root.
                        Empty string means the repository root.

        Returns:
                A newline-separated list of entries. Each line is one of:
                ``[DIR] relative/path`` or
                ``[FILE] relative/path (N lines)``.
        """
        Logger.log(f"[Tool Call]: Listing directory at path '{path}'.")
        target_dir = os.path.join(self.base_dir, path)
        
        if not os.path.exists(target_dir):
            return f"Error: Directory '{path}' does not exist."
        if not os.path.isdir(target_dir):
            return f"Error: '{path}' is not a directory."

        output = []
        skip_dirs = {'.git', '__pycache__', '.venv', '.github'}
        
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            rel_path = os.path.relpath(root, target_dir)
            
            rel_path_base = os.path.relpath(root, self.base_dir)
            prefix = ""
            if rel_path_base != ".":
                prefix = rel_path_base + os.sep
            
            for d in dirs:
                output.append(f"[DIR] {prefix}{d}")
            for f in files:
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                        line_count = sum(1 for _ in file)
                    output.append(f"[FILE] {prefix}{f} ({line_count} lines)")
                except Exception as e:
                    continue
            
            if rel_path != ".":
                dirs[:] = []
                
        if not output:
            return "Directory is empty."
            
        return "\n".join(sorted(output, key=lambda x: x.split(" ", 2)[1].lower()))

    def read_file_snippet(self, file_path: str, start_line: int, end_line: int) -> str:
        """Read a portion of a file with line numbers.

        Use this tool to inspect relevant sections of source files
        (for example module docstrings, function definitions, or
        example code) before constructing the final example script.

        Args:
            file_path: Path to the file, relative to the repository
                root.
            start_line: The starting line number (1-based).
            end_line: The ending line number (1-based, inclusive).

        Returns:
            Numbered lines from the file in the format
            ``<line_number>: <line_content>`` on each line, or a
            human-readable error message.
        """
        Logger.log(f"[Tool Call]: Reading file snippet from '{file_path}' lines {start_line}-{end_line}.")
        target_path = os.path.join(self.base_dir, file_path)

        if not os.path.exists(target_path):
            return f"Error: File '{file_path}' does not exist."

        if not os.path.isfile(target_path):
            return f"Error: '{file_path}' is not a file."

        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if start_line < 1:
                start_line = 1

            if end_line > len(lines):
                end_line = len(lines)

            if start_line > end_line:
                return f"Error: Start line {start_line} is greater than end line {end_line}."

            snippet = lines[start_line-1:end_line]

            # Add line numbers to the output
            numbered_snippet = []
            for i, line in enumerate(snippet, start=start_line):
                numbered_snippet.append(f"{i}: {line.rstrip()}")

            return "\n".join(numbered_snippet)

        except Exception as e:
            return f"Error reading file: {str(e)}"
        
    def grep_search_file(self, pattern: str, file_path: str) -> str:
        """Search for a plain-text pattern inside a single file.

        This is useful for locating functions, classes, "main" blocks,
        or usage examples that should be mirrored in the generated
        example script.

        Args:
            pattern: The plain-text string to search for. It should fit
                within a single line (no regular expressions).
            file_path: Path to the file to search in, relative to the
                repository root.

        Returns:
            One match per line in the format
            ``<line_number>: <line_content>``. If there are no matches
            or an error occurs, a human-readable message is returned
            instead.
        """
        Logger.log(f"[Tool Call]: Grep searching for pattern '{pattern}' in file '{file_path}'.")
        target_path = os.path.join(self.base_dir, file_path)

        if not os.path.exists(target_path):
            return f"Error: File '{file_path}' does not exist."
        if not os.path.isfile(target_path):
            return f"Error: '{file_path}' is not a file."

        results = []
        
        try:
            with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern in line:
                        results.append(f"{line_num}: {line.strip()}")
        except Exception as e:
            return f"Error reading file: {str(e)}"
                    
        if not results:
            return f"No matches found for '{pattern}' in '{file_path}'."
            
        return "\n".join(results)

    def grep_search_directory(self, pattern: str, path: str = "") -> str:
        """Search recursively for a plain-text pattern in many files.

        Use this to find where important functions, classes, or CLI
        entry points are defined across the repository so you can design
        a realistic example script.

        Args:
            pattern: The plain-text string to search for. It should fit
                within a single line (no regular expressions).
            path: Directory path to search in, relative to the
                repository root. Empty string means the repository root.

        Returns:
            One match per line in the format
            ``<file_path>:<line_number>: <line_content>`` relative to
            the repository root, or a message if no matches are found or
            an error occurs.
        """
        Logger.log(f"[Tool Call]: Grep searching for pattern '{pattern}' in directory '{path}'.")
        target_dir = os.path.join(self.base_dir, path)

        if not os.path.exists(target_dir):
            return f"Error: Directory '{path}' does not exist."
        if not os.path.isdir(target_dir):
            return f"Error: '{path}' is not a directory."

        results = []
        
        for root, _, files in os.walk(target_dir):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern in line:
                                rel_path = os.path.relpath(full_path, self.base_dir)
                                results.append(f"{rel_path}:{line_num}: {line.strip()}")
                except Exception:
                    continue
                    
        if not results:
            return f"No matches found for '{pattern}' in '{path}'."
            
        return "\n".join(results)
