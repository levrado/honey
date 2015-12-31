import socket

import protocols


class _Protocol(protocols.Protocol):

    def __init__(self, RequestHandlerClass):
        super().__init__()
        self._RequestHandlerClass = RequestHandlerClass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Server(_Protocol):

    def __init__(self, host, port, RequestHandlerClass):
        super().__init__(RequestHandlerClass)
        self._host = host
        self._port = port
        self._bind()

    def _bind(self):
        self.socket.bind((self._host, self._port))
        self.socket.listen(5)

    def handle_connection_made(self):
        return self._accept_new_connection()

    def handle_data_received(self, socket_with_new_data):
        data = socket_with_new_data.recv(1024)
        self._RequestHandlerClass.got_new_data(data)

    def _accept_new_connection(self):
        connection, address = self.socket.accept()
        connection.setblocking(0)
        self._RequestHandlerClass = self._RequestHandlerClass(connection, address)

        return connection, address
