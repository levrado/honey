import select
import sys
import traceback

import protocols.tcp
import reactor.promise
import utils


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Reactor(metaclass=Singleton):

    def __init__(self):

        self._data_received = {}
        self._connections = []
        self._servers = {}
        self._clients = {}
        self._to_fulfill = []
        self._running = False

        self._logger = utils.Logger('Reactor')

    def _handle_new_connection(self, server):

        # wait to accept a connection - blocking call
        connection, addr = server.handle_connection_made()

        # set the socket object to none blocking so it will not get our thread stuck
        self._connections.append(connection)
        self._clients[connection] = server
        self._logger.debug('Got a new client, adding to server={0} client={1}'.format(server, connection))

    def _handle_new_message_received(self, connection):
        self._clients[connection].handle_data_received(connection)
        # self._logger.debug('Got new data from client={0}'.format(connection))

    def handle_acceptable_object(self, acceptable_object):
        if acceptable_object == sys.stdin:

            # handle standard input
            junk = sys.stdin.readline()

            self._logger.debug('Got stdin, closing the server')

            # stop the server
            self._running = False
        elif self._servers.get(acceptable_object) is not None:
            self._handle_new_connection(self._servers.get(acceptable_object))
        else:
            self._handle_new_message_received(acceptable_object)

    def add_server(self, host, port, handler):
        tcp_server = protocols.tcp.Server(host, port, handler)
        self._servers[tcp_server.socket] = tcp_server
        self._connections.append(tcp_server.socket)
        self._logger.debug('Added a new tcp server to reactor server={0}'.format(tcp_server))

    def remove_connection(self, connection):
        self._connections.remove(connection)
        self._logger.debug('Removed a connection scoket={0}'.format(connection))

    @property
    def connections(self):
        return self._connections

    @property
    def running(self):
        return self._running

    @property
    def to_fulfill(self):
        return self._to_fulfill

    def set_running(self, new_value):
        self._running = new_value

    def add_fulfiller(self, promise_to_fulfill, *args, **kwargs):
        self._to_fulfill.append((promise_to_fulfill, args, kwargs))

    def run(self):
        '''
        The heart of our async logic, process new connections, new messages from existing connections
        or complete reading the data from receiving messages
        '''
        self.set_running(True)
        try:
            while self.running:
                '''
                Project Goals:
    
                Accept a set of file descriptors you are interested in performing I/O with.
                Tell you, repeatedly, when any file descriptors are ready for I/O.
                Provide lots of nice abstractions to help you use the reactor with the least amount of effort.
                Provide implementations of UDP and TCP protocols that you can use out of the box.
    
                '''
                self.handle_io()
                self.handle_promises()

        except (KeyboardInterrupt, SystemExit):
            pass

        except Exception as e:
            self._logger.warn(str(e))
            traceback.print_tb(sys.exc_info()[2])

        finally:
            self._logger.info('Stopping reactor (Should be a cleanup)')

    def handle_promises(self):
        try:
            next_to_fulfill, args, kwargs = self.to_fulfill.pop()
            next_to_fulfill(*args, **kwargs)
        except IndexError:
            pass

    def handle_io(self):
        input_ready = None
        select_connections_list = self.connections + [sys.stdin]

        for connection in select_connections_list:
            try:
                if connection._closed:
                    self.remove_connection(connection)
            except AttributeError:
                pass

        # dont wait at all, check and continue without blocking
        try:
            input_ready, output_ready, except_ready = select.select(select_connections_list, [], [], 0)

        except ValueError:
            pass

        # did we got anything from one of the file descriptors?
        if input_ready:
            for acceptable_object in input_ready:
                self.handle_acceptable_object(acceptable_object)


def run():
    main_reactor.run()


def add_tcp_server(host, port, handler):
    main_reactor.add_server(host, port, handler)


def add_fulfiller(promise_to_fulfill, *args, **kwargs):
    main_reactor.add_fulfiller(promise_to_fulfill, *args, **kwargs)


main_reactor = Reactor()
