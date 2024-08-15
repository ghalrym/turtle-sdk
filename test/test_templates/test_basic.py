from langchain_core.messages import HumanMessage, AIMessage

from templates.basic.agent import BasicBot
from unittest.mock import MagicMock

mock_llama_model = MagicMock()
mock_llama_model.invoke.return_value = AIMessage("llama")


def test_basic_bot():
    bot = BasicBot()
    bot.invoke(send_message="Hello World")
    bot.turtle_tools[1].model = mock_llama_model
    assert bot._state._state == {
        "send_message": "Hello World",
        "chat_history": [HumanMessage(content="Hello World")],
    }
    bot.trigger("get_chat")
    assert bot._state._state == {
        "send_message": "Hello World",
        "ai_message": "llama",
        "chat_history": [HumanMessage(content="Hello World"), AIMessage("llama")],
    }
