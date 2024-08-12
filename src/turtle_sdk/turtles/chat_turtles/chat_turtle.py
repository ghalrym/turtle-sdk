from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from bale_of_turtles import use_state, use_trigger
from bale_of_turtles.tool_turtle import TurtleTool

from turtle_sdk.turtles.turtle_tool_maker import TurtleToolMaker


class ChatTurtle(TurtleTool):
    def __init__(self):
        super(TurtleTool, self).__init__()
        self.chat_state: list[BaseMessage] = []


class ChatTurtleMaker(TurtleToolMaker):

    def make(
        self,
        human_message_key: str,
        ai_message_key: str,
        system_message_key: str,
        chat_history_key: str,
        **kwargs,
    ) -> ChatTurtle:

        class _ChatTurtle(ChatTurtle):

            @use_state(self._make_fn_key("chat-system-message"), [system_message_key])
            def system_message_input(self, **kwargs):
                system_message = kwargs.get(system_message_key, None)
                if isinstance(system_message, SystemMessage):
                    self.chat_state.append(system_message)
                elif isinstance(system_message, str):
                    self.chat_state.append(SystemMessage(content=system_message))
                else:
                    raise Exception(
                        "Invalid system message type, {}".format(type(system_message))
                    )
                self.update_state(**{chat_history_key: self.chat_state})

            # noinspection DuplicatedCode
            @use_state(self._make_fn_key("chat-user-message"), [human_message_key])
            def user_message_input(self, **kwargs):
                human_message = kwargs.get(human_message_key, None)
                if isinstance(human_message, SystemMessage):
                    self.chat_state.append(human_message)
                elif isinstance(human_message, str):
                    self.chat_state.append(HumanMessage(human_message))
                else:
                    raise Exception(
                        "Invalid system message type, {}".format(type(human_message))
                    )
                self.update_state(**{chat_history_key: self.chat_state})

            # noinspection DuplicatedCode
            @use_state(self._make_fn_key("ai-message"), [ai_message_key])
            def ai_message_input(self, **kwargs):
                ai_message = kwargs.get(human_message_key, None)
                if isinstance(ai_message, SystemMessage):
                    self.chat_state.append(ai_message)
                elif isinstance(ai_message, str):
                    self.chat_state.append(HumanMessage(ai_message))
                else:
                    raise Exception(
                        "Invalid system message type, {}".format(type(ai_message))
                    )
                self.update_state(**{chat_history_key: self.chat_state})

        return _ChatTurtle()
