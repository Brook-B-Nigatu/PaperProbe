import inspect

from langchain_core.tools import StructuredTool


class ToolProviderBase:
    def get_tool_list(self) -> list:
        tools = []
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, func in members:
            if name.startswith("_") or name == "get_tool_list":
                continue
            tool = StructuredTool.from_function(
                func=func, name=name, description=func.__doc__ or f"Tool for {name}"
            )
            tools.append(tool)
        return tools
