from langchain_core.messages import HumanMessage
from src.constructor.constructor_model import ConstructorModel
from src.constructor.tool_aware import create_tool_aware_agent

from src.core.Logger import Logger


def get_chat_model():
    """Returns an instance of the chat model used in the application."""
    return ConstructorModel()


def call_llm(prompt: str) -> str:
    """Calls the language model with the given prompt and returns the response.

    Args:
        prompt (str): The prompt to send to the language model.

    Returns:
        str: The response from the language model.
    """
    model = get_chat_model()
    return model.invoke([HumanMessage(content=prompt)]).content


def execute_agentic_task(tools: list, messages: list) -> str:
    """Executes an agentic task using the provided tools and messages.

    Args:
        tools (list): A list of tools available to the agent.
        messages (list): A list of messages to set up the agent's state.

    Returns:
        str: The final response from the agent after executing the task.
    """
    try:
        model = get_chat_model()
    except Exception:
        Logger.log(
            "Failed to initialize the chat model. Please make sure you've set the necessary environment variables."
        )
        return ""
    agent = create_tool_aware_agent(model=model, tools=tools)

    result = agent.invoke(agent.setup_state(messages=messages))

    return result["messages"][-1].content
