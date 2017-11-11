import protocols.tcp
import reactor


class TcpHandlerFactory(protocols.tcp.HandlerFactory):

    def on_connection_established(self, connection, client_address):
        tcp_handler = TcpHandler(connection, client_address)
        return tcp_handler


class TcpHandler(protocols.tcp.Handler):

    def __init__(self, connection, client_address):
        '''
        called when a new client connects

        :param connection: socket object
        :param client_address: address ip and port
        '''

        self._data = []

        # sending message to connected client
        welcome_message = 'Welcome to the server {0}. Type something and hit enter\n'.format(client_address)
        connection.send(bytes(welcome_message, 'UTF-8'))

    def got_new_data(self, data):
        '''
        :param data: the data from the client
        :return: None
        '''
        print(data)


reactor.add_tcp_server('', 8888, TcpHandlerFactory())

reactor.run()
