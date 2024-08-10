import logging

from bale_of_turtles import use_state
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage

from .llm_turtle import LlmTurtle

logger = logging.getLogger(__name__)


class LlamaTurtle(LlmTurtle):
    __slots__ = ("_model",)

    def __init__(self, name: str):
        super().__init__(name)
        self._model = ChatOllama(model=name)

    @use_state("llm-message", ["turtle_human_message"])
    def invoke(
        self,
        turtle_human_message: BaseMessage | None = None,
        turtle_llm_message_history: list[BaseMessage] | None = None,
        *args,
        **kwargs,
    ):
        if not turtle_human_message:
            return
        logger.info(f"User: {turtle_llm_message_history[-1].content}")
        response = self._model.invoke(turtle_llm_message_history)
        logger.info(f"Llama: {response.content}")
        self.update_state(turtle_ai_message=response)
