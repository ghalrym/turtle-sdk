import logging
from socket import socket

from bale_of_turtles import use_state

from turtle_sdk.turtles.socket_turtles._communicator import ServerSocketTurtleTool
from turtle_sdk.turtles.turtle_tool_maker import make_fn_key

logger = logging.getLogger(__name__)


class ServerSocketTurtle(ServerSocketTurtleTool):

    def __init__(self, address: str, port: int, receiver_key: str, sender_key: str):
        super().__init__(address, port)
        self.currently_responding = False
        self.receiver_key = receiver_key
        self.sender_key = sender_key

        self.sender = use_state(make_fn_key("socket-sender"), [sender_key])(
            self._sender
        )

    def handle_connection(self, _socket: socket):
        try:
            while True:
                self.currently_responding = True
                self.update_state(
                    **{self.receiver_key: self.recieve_data(self.client_connection)}
                )
                while self.currently_responding:
                    ...
        except ConnectionResetError:
            logger.info("connection reset")

    def _sender(self, **sender_kwargs):
        send_chunk = sender_kwargs.get(self.sender_key)
        if not isinstance(send_chunk, bytes):
            raise Exception("send_chunk must be bytes")
        self.send_data(send_chunk, self.client_connection)
        self.currently_responding = False
