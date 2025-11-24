from constructor.constructor_model import ConstructorModel
from langchain_core.messages import HumanMessage

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