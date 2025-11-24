import ast
import os
from .tool_provider_base import ToolProviderBase

class CodeAnalysisToolsProvider(ToolProviderBase):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def get_signatures(self, file_path: str) -> str:
        """
        Parses a python file and returns a string containing the signatures of classes and functions,
        including their docstrings.
        """
        full_path = os.path.join(self.base_dir, file_path) if not os.path.isabs(file_path) else file_path
        
        if not os.path.exists(full_path):
            return f"Error: File not found at {full_path}"
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception as e:
            return f"Error parsing file {file_path}: {str(e)}"
            
        results = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                results.append(self._format_function(node))
            elif isinstance(node, ast.ClassDef):
                results.append(self._format_class(node))
                
        return "\n\n".join(results)

    def _format_function(self, node, indent_level=0) -> str:
        indent = "    " * indent_level
        
        decorators = []
        if hasattr(ast, 'unparse'):
            for decorator in node.decorator_list:
                try:
                    dec_str = f"@{ast.unparse(decorator)}"
                    decorators.append(f"{indent}{dec_str}")
                except Exception:
                    pass

        def_prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        
        args_str = "..."
        if hasattr(ast, 'unparse'):
            try:
                args_str = ast.unparse(node.args)
            except Exception:
                pass

        returns_str = ""
        if node.returns and hasattr(ast, 'unparse'):
            try:
                returns_str = f" -> {ast.unparse(node.returns)}"
            except Exception:
                pass

        sig_line = f"{indent}{def_prefix} {node.name}({args_str}){returns_str}:"
        
        docstring = ast.get_docstring(node)
        if docstring:
            doc_lines = docstring.splitlines()
            formatted_doc = f'\n{indent}    """'
            if len(doc_lines) > 0:
                formatted_doc += f"\n{indent}    {doc_lines[0]}"
                for line in doc_lines[1:]:
                    formatted_doc += f"\n{indent}    {line}"
            formatted_doc += f'\n{indent}    """'
            return "\n".join(decorators + [sig_line + formatted_doc])
        else:
            return "\n".join(decorators + [sig_line])

    def _format_class(self, node) -> str:
        decorators = []
        if hasattr(ast, 'unparse'):
            for decorator in node.decorator_list:
                try:
                    dec_str = f"@{ast.unparse(decorator)}"
                    decorators.append(dec_str)
                except Exception:
                    pass

        bases = []
        if hasattr(ast, 'unparse'):
            for base in node.bases:
                try:
                    bases.append(ast.unparse(base))
                except Exception:
                    pass
        
        base_str = f"({', '.join(bases)})" if bases else ""
        class_line = f"class {node.name}{base_str}:"
        
        docstring = ast.get_docstring(node)
        parts = decorators + [class_line]
        
        if docstring:
            doc_lines = docstring.splitlines()
            formatted_doc = '    """'
            if len(doc_lines) > 0:
                formatted_doc += f"\n    {doc_lines[0]}"
                for line in doc_lines[1:]:
                    formatted_doc += f"\n    {line}"
            formatted_doc += '\n    """'
            parts.append(formatted_doc)
            
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parts.append(self._format_function(item, indent_level=1))
                
        return "\n".join(parts)
