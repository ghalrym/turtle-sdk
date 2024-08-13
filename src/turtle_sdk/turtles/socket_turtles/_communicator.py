import logging

from bale_of_turtles import TurtleTool, ActionTurtle
from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable


ClientHandler = Callable[[bytes], bytes]
RecieveDataFunc = Callable[[], bytes]
SendDataFunc = Callable[[bytes], None]

logger = logging.getLogger(__name__)


class _ComunicatorMixins:
    # __slots__ = ("connection", "_address", "_port")

    def __init__(self, address: str, port: int):
        self.connection = socket(AF_INET, SOCK_STREAM)
        self._address = address
        self._port = port

    def recieve_data(self, conn: socket | None = None) -> bytes:
        connection = conn if conn else self.connection
        connection.sendall(b"length")
        data_size = int(connection.recv(1024).decode())
        connection.sendall(b"message")
        chunk = connection.recv(data_size)
        logger.info("Received message: {}".format(chunk))
        return chunk

    def send_data(self, chunk: bytes, conn: socket | None = None) -> None:
        logger.info("Sending message: {}".format(chunk.decode("utf-8")))
        connection = conn if conn else self.connection
        connection.recv(1024)
        connection.sendall(f"{len(chunk)}".encode("utf-8"))
        connection.recv(1024)
        connection.sendall(chunk)


class ClientSocketTurtleTool(_ComunicatorMixins, TurtleTool):

    def __init__(self, address: str, port: int):
        _ComunicatorMixins.__init__(self, address, port)
        TurtleTool.__init__(self)

    def connect(self):
        return self.connection.connect((self._address, self._port))


class ServerSocketTurtleTool(_ComunicatorMixins, ActionTurtle):

    def __init__(self, address: str, port: int):
        _ComunicatorMixins.__init__(self, address, port)
        ActionTurtle.__init__(self)
        self.client_connection = None

    def run_server(self, _socket: socket, conn: socket): ...

    def invoke(self, **invoke_kwargs):
        while True:
            with socket(AF_INET, SOCK_STREAM) as s:
                s.bind((self._address, self._port))
                s.listen()
                self.client_connection, addr = s.accept()
                logger.info("connection from", addr)
                self.run_server(s)
