import socket
import abc

import protocols


class _Protocol(protocols.Protocol):

    def __init__(self, request_factory):
        '''
        Init TCP/IP Protocol with handler class
        :param RequestHandlerClass: class that handles a connection
        :return: None
        '''
        super().__init__()
        self._handler_factory = request_factory
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class HandlerFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def on_connection_established(self, connection, client_address):
        pass


class Handler(metaclass=abc.ABCMeta):
    '''
    Abstract class
    '''

    @abc.abstractmethod
    def __init__(self, connection, client_address):
        pass

    @abc.abstractmethod
    def got_new_data(self, data):
        '''
        :param data: data to handle
        :return: None
        '''
        pass


class Server(_Protocol):

    def __init__(self, host, port, handler_factory):
        '''
        :param host:
        :param port:
        :param handler_factory:
        :return:
        '''
        super().__init__(handler_factory)
        self._host = host
        self._port = port
        self._bind()
        self._handlers = {}

    def _bind(self):
        self.socket.bind((self._host, self._port))
        self.socket.listen(5)

    def handle_connection_made(self):
        return self._accept_new_connection()

    def _handle_closed_connection(self, closed_socket):
        print("Closed Socket")
        del self._handlers
        closed_socket.close()

    def handle_data_received(self, socket_with_new_data):
        data = socket_with_new_data.recv(1)
        if data:
            self._handlers[socket_with_new_data].got_new_data(data)
        else:
            self._handle_closed_connection(socket_with_new_data)

    def _accept_new_connection(self):
        connection, address = self.socket.accept()
        connection.setblocking(0)

        # call the handler factory's connection established function with connection and address
        handler = self._handler_factory.on_connection_established(connection, address)
        self._handlers[connection] = handler

        return connection, address
