import logging

from langchain_community.chat_models import ChatOllama

from .llm_turtle import ChatLlmTurtleMaker

logger = logging.getLogger(__name__)


class ChatOllamaTurtleMaker(ChatLlmTurtleMaker):
    __slots__ = ("_model",)

    def __init__(self, model_name: str):
        super(ChatLlmTurtleMaker, self).__init__(ChatOllama(model=model_name))
