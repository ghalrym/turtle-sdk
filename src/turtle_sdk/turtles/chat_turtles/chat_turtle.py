from types import MethodType

from bale_of_turtles import use_state
from bale_of_turtles.tool_turtle import TurtleTool
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

from turtle_sdk.turtles.turtle_tool_maker import make_fn_key


class ChatTurtle(TurtleTool):
    __slots__ = (
        "chat_state",
        "human_message_key",
        "ai_message_key",
        "system_message_key",
        "chat_history_key",
        "system_message_input",
        "user_message_input",
        "ai_message_input",
    )

    def __init__(
        self,
        human_message_key: str,
        ai_message_key: str,
        system_message_key: str,
        chat_history_key: str,
    ):
        super(TurtleTool, self).__init__()

        # Set up variables
        self.chat_state: list[BaseMessage] = []
        self.ai_message_key = ai_message_key
        self.chat_history_key = chat_history_key
        self.human_message_key = human_message_key

        # Setup methods
        self.system_message_input = use_state(
            make_fn_key("chat-system-message"), [system_message_key]
        )(self._system_message_input)
        self.user_message_input = use_state(
            make_fn_key("chat-user-message"), [human_message_key]
        )(self._user_message_input)
        self.ai_message_input = use_state(make_fn_key("ai-message"), [ai_message_key])(
            self._ai_message_input
        )

    def _system_message_input(self, **kwargs):
        system_message = kwargs.get(self.system_message_key, None)
        if isinstance(system_message, SystemMessage):
            self.chat_state.append(system_message)
        elif isinstance(system_message, str):
            self.chat_state.append(SystemMessage(content=system_message))
        else:
            raise Exception(
                "Invalid system message type, {}".format(type(system_message))
            )
        self.update_state(**{self.chat_history_key: self.chat_state})

    def _user_message_input(self, **kwargs):
        human_message = kwargs.get(self.human_message_key, None)
        if isinstance(human_message, SystemMessage):
            self.chat_state.append(human_message)
        elif isinstance(human_message, str):
            self.chat_state.append(HumanMessage(human_message))
        else:
            raise Exception(
                "Invalid system message type, {}".format(type(human_message))
            )
        self.update_state(**{self.chat_history_key: self.chat_state})

    def _ai_message_input(self, **kwargs):
        ai_message = kwargs.get(self.ai_message_key, None)
        if isinstance(ai_message, AIMessage):
            self.chat_state.append(ai_message)
        elif isinstance(ai_message, str):
            self.chat_state.append(AIMessage(ai_message))
        else:
            raise Exception("Invalid system message type, {}".format(type(ai_message)))
        self.update_state(**{self.chat_history_key: self.chat_state})
