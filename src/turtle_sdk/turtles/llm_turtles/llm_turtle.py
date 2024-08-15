import logging

from bale_of_turtles.tool_turtle import TurtleTool
from langchain_core.language_models import BaseChatModel

from bale_of_turtles import use_trigger
from langchain_community.chat_models import ChatOllama

from ..turtle_tool_maker import TurtleToolMaker, make_fn_key

logger = logging.getLogger(__name__)


class ChatLlmTurtle(TurtleTool):
    __slots__ = ("model", "invoke", "message_history_key", "response_key")

    def __init__(
        self,
        model: BaseChatModel,
        trigger_response_key: str,
        message_history_key: str,
        response_key: str,
    ):
        super(TurtleTool, self).__init__()
        self.model = model
        self.invoke = use_trigger(trigger_response_key)(self._invoke)
        self.message_history_key = message_history_key
        self.response_key = response_key

    def _invoke(self, **kwargs):
        message_history = kwargs.get(self.message_history_key, [])
        if not message_history:
            raise Exception("Message history is empty")
        response = self.model.invoke(message_history)

        self.update_state(**{self.response_key: response.content})


class ChatLlmTurtleMaker(TurtleToolMaker):
    __slots__ = ("_model",)

    def __init__(self, model: BaseChatModel):
        super(TurtleToolMaker, self).__init__()
        self._model = model

    def make(
        self,
        trigger_response_key: str,
        message_history_key: str,
        response_key: str,
        **kwargs,
    ) -> ChatLlmTurtle:
        return ChatLlmTurtle(
            self._model, trigger_response_key, message_history_key, response_key
        )
