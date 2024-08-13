import logging

from bale_of_turtles import use_state
from socket import socket
from turtle_sdk.turtles.socket_turtles._communicator import (
    ServerSocketTurtleTool,
    ClientHandler,
)
from turtle_sdk.turtles.turtle_tool_maker import TurtleToolMaker

logger = logging.getLogger(__name__)


class ServerSocketTurtleMaker(TurtleToolMaker):

    def __init__(self, address: str, port: int, client_handler: ClientHandler):
        super().__init__()
        self._address = address
        self._port = port
        self._client_handler = client_handler

    def make(
        self, receiver_key: str, sender_key: str, **kwargs
    ) -> ServerSocketTurtleTool:
        class _ServerSocketTurtleTool(ServerSocketTurtleTool):

            def __init__(self, address: str, port: int):
                super().__init__(address, port)
                self.currently_responding = False

            def handle_connection(self, _socket: socket):
                try:
                    while True:
                        self.currently_responding = True
                        self.update_state(
                            **{receiver_key: self.recieve_data(self.client_connection)}
                        )
                        while self.currently_responding:
                            ...
                except ConnectionResetError:
                    logger.info("connection reset")

            @use_state(self._make_fn_key("socket-sender"), [sender_key])
            def sender(self, **sender_kwargs):
                send_chunk = sender_kwargs.get(sender_key)
                if not isinstance(send_chunk, bytes):
                    raise Exception("send_chunk must be bytes")
                self.send_data(send_chunk, self.client_connection)
                self.currently_responding = False

        return _ServerSocketTurtleTool(self._address, self._port)
