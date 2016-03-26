import protocols.tcp
import reactor


class TcpHandler(protocols.tcp.Handler):

    def __init__(self, connection, client_address):
        '''
        called when a new client connects

        :param connection: socket object
        :param client_address: address ip and port
        :return: None
        '''
        # sending message to connected client
        connection.send(bytes('Welcome to the server. Type something and hit enter\n', 'UTF-8'))

    def got_new_data(self, data):
        '''
        :param data: the data from the client
        :return: None
        '''
        print(data)


reactor.add_tcp_server('', 8888, TcpHandler)

reactor.run()