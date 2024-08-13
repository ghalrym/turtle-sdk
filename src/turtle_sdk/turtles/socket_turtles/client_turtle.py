import logging

from bale_of_turtles import use_state

from turtle_sdk.turtles.socket_turtles._communicator import ClientSocketTurtleTool
from turtle_sdk.turtles.turtle_tool_maker import TurtleToolMaker

logger = logging.getLogger(__name__)


class ClientSocketTurtleMaker(TurtleToolMaker):

    def __init__(self, address: str, port: int):
        super().__init__()
        self._address = address
        self._port = port

    def make(
        self, message_key: str, response_key: str, **kwargs
    ) -> ClientSocketTurtleTool:

        class _SocketTurtleTool(ClientSocketTurtleTool):

            def __init__(self, address: str, port: int):
                super().__init__(address, port)
                # Connect to server
                logger.info("Connecting to {}:{}".format(self._address, self._port))
                self.connect()

            @use_state(self._make_fn_key("client-socket-turtle"), [message_key])
            def invoke(self, **invoke_kwargs):
                bytes_message = invoke_kwargs.get(message_key)
                if bytes_message is None or not isinstance(bytes_message, bytes):
                    raise ValueError("Message is missing {}".format(message_key))

                self.send_data(bytes_message)  # Send message
                response = self.recieve_data()  # Get Response
                self.update_state(**{response_key: response})  # Update State

        return _SocketTurtleTool(self._address, self._port)
