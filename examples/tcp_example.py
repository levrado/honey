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
        self._acc = None
        # sending message to connected client
        connection.send(bytes('Welcome to the server. Type something and hit enter\n', 'UTF-8'))

    def got_new_data(self, data):
        '''
        :param data: the data from the client
        :return: None
        '''
        data_to_print = yield self.accumulate_data(data)
        if len(data_to_print) > 10:
            print (data_to_print)
            print (self._acc)

    def accumulate_data(self, data):
        self._acc += data

        # long process
        for x in range(9):
            yield x

reactor.add_tcp_server('', 8888, TcpHandler)

data = yield from get_full_data

reactor.run()