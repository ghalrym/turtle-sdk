import logging

from bale_of_turtles import use_state

from turtle_sdk.turtles.socket_turtles._communicator import ClientSocketTurtleTool
from turtle_sdk.turtles.turtle_tool_maker import make_fn_key

logger = logging.getLogger(__name__)


class ClientSocketTurtle(ClientSocketTurtleTool):

    def __init__(self, address: str, port: int, message_key: str, response_key: str):
        super().__init__(address, port)
        self.message_key = message_key
        self.response_key = response_key

        self.invoke = use_state(make_fn_key("client-socket-turtle"), [message_key])(
            self._invoke
        )
        # Connect to server
        logger.info("Connecting to {}:{}".format(self._address, self._port))
        self.connect()

    def _invoke(self, **invoke_kwargs):
        bytes_message = invoke_kwargs.get(self.message_key)
        if bytes_message is None or not isinstance(bytes_message, bytes):
            raise ValueError("Message is missing {}".format(self.message_key))

        self.send_data(bytes_message)  # Send message
        response = self.recieve_data()  # Get Response
        self.update_state(**{self.response_key: response})  # Update State
