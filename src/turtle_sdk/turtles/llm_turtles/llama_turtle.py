import logging

from langchain_community.chat_models import ChatOllama

from .llm_turtle import ChatLlmTurtle

logger = logging.getLogger(__name__)


class ChatOllamaTurtle(ChatLlmTurtle):
    __slots__ = ("_model",)

    def __init__(
        self,
        model_name: str,
        response_key: str,
        trigger_response_key: str,
        message_history_key: str,
    ):
        super().__init__(
            ChatOllama(model=model_name),
            trigger_response_key,
            message_history_key,
            response_key,
        )
