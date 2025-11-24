import os
from .tool_provider_base import ToolProviderBase

class FileSystemToolsProvider(ToolProviderBase):

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def list_directory(self, path: str = "") -> str:
        """Lists the files and directories in the given path up to a depth of 2.
        Directories can be further explored using this tool again. Files come with
        the number of lines in them, and they can be read using the read_file_snippet tool.

        Args:
            path: Path to the directory. Empty string means base directory.
        Returns:
            The list of files and directories upto a depth of 2.
            [DIR] indicates a directory and [FILE] indicates a file.
        """
        target_dir = os.path.join(self.base_dir, path)
        
        if not os.path.exists(target_dir):
            return f"Error: Directory '{path}' does not exist."
        if not os.path.isdir(target_dir):
            return f"Error: '{path}' is not a directory."

        output = []
        
        for root, dirs, files in os.walk(target_dir):
            rel_path = os.path.relpath(root, target_dir)
            
            rel_path_base = os.path.relpath(root, self.base_dir)
            prefix = ""
            if rel_path_base != ".":
                prefix = rel_path_base + os.sep
            
            for d in dirs:
                output.append(f"[DIR] {prefix}{d}")
            for f in files:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    line_count = sum(1 for _ in file)
                output.append(f"[FILE] {prefix}{f} ({line_count} lines)")
            
            if rel_path != ".":
                dirs[:] = []
                
        if not output:
            return "Directory is empty."
            
        return "\n".join(sorted(output, key=lambda x: x.split(" ", 2)[1].lower()))

    def read_file_snippet(self, file_path: str, start_line: int, end_line: int) -> str:
        """Return numbered lines from a file between `start_line` and `end_line`.

        Args:
            file_path: Path to the file
            start_line: The starting line number (1-based).
            end_line: The ending line number (1-based, inclusive).
        
        Returns:
            Numbered lines from the file.
        """
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
        """Searches for a given string in a specific file.

        Args:
            pattern: The string to search for. Should be a simple string that fits in a single line.
            file_path: The path to the file to search in.

        Returns:
            Line numbers and content where the pattern was found.
            Each result is in the format: <line_number>: <line_content>
        """
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
        """Searches for a given string in all files contained within this directory.

        Args:
            pattern: The string to search for. Should be a simple string that fits in a single line.
            path: The directory path to search in. Empty string means base directory.

        Returns:
            File paths and line numbers where the pattern was found.
            Each result is in the format: <file_path>:<line_number>: <line_content>
        """
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
