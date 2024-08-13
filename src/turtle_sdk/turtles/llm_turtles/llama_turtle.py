import logging

from bale_of_turtles import use_trigger
from langchain_community.chat_models import ChatOllama

from .llm_turtle import LlmTurtle
from ..turtle_tool_maker import TurtleToolMaker

logger = logging.getLogger(__name__)


class ChatLlamaTurtle(LlmTurtle): ...


class ChatLlamaTurtleMaker(TurtleToolMaker):
    __slots__ = ("_model",)

    def __init__(self, model_name: str):
        super(TurtleToolMaker, self).__init__()
        self._model = ChatOllama(model=model_name)

    def make(
        self,
        trigger_response_key: str,
        message_history_key: str,
        response_key: str,
        **kwargs,
    ) -> ChatLlamaTurtle:

        class _LlamaTurtle(ChatLlamaTurtle):
            def __init__(self, model: ChatOllama):
                super(ChatLlamaTurtle, self).__init__()
                self.model = model

            @use_trigger(trigger_response_key)
            def invoke(self, **kwargs):
                message_history = kwargs.get(message_history_key, [])
                if not message_history:
                    raise Exception("Message history is empty")
                response = self.model.invoke(message_history)

                self.update_state(**{response_key: response.content})

        return _LlamaTurtle(self._model)
