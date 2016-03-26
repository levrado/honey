import socket
import abc

import protocols


class _Protocol(protocols.Protocol):

    def __init__(self, RequestHandlerClass):
        '''
        Init TCP/IP Protocol with handler class
        :param RequestHandlerClass: class that handles a connection
        :return: None
        '''
        super().__init__()
        self._RequestHandlerClass = RequestHandlerClass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Handler(object):
    '''
    Abstract class
    '''

    __metadata__ = abc.ABCMeta

    def __init__(self):
        pass

    def got_new_data(self, data):
        '''
        :param data: data to handle
        :return: None
        '''
        pass

class Server(_Protocol):

    def __init__(self, host, port, RequestHandlerClass):
        '''
        :param host:
        :param port:
        :param RequestHandlerClass:
        :return:
        '''
        super().__init__(RequestHandlerClass)
        self._host = host
        self._port = port
        self._bind()
        self._handlers = {}

    def _bind(self):
        self.socket.bind((self._host, self._port))
        self.socket.listen(5)

    def handle_connection_made(self):
        return self._accept_new_connection()

    def handle_data_received(self, socket_with_new_data):
        data = socket_with_new_data.recv(1024)
        if data:
            self._handlers[socket_with_new_data].got_new_data(data)

    def _accept_new_connection(self):
        connection, address = self.socket.accept()
        connection.setblocking(0)

        # call class constructor with the accepted connection and address of client
        self._handlers[connection] = self._RequestHandlerClass(connection, address)

        return connection, address
