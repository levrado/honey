import socket
import select
import sys
import traceback
import logging


class Logger():

    def __init__(self, name):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def info(self, msg):
        self._logger.info(msg)

    def warn(self, msg):
        self._logger.warn(msg)

    def debug(self, msg):
        self._logger.debug(msg)

    def error(self, msg):
        self._logger.error(msg)


class Reactor(object):

    def __init__(self, host, port, reactor_num=1):
        self._host = host
        self._port = port

        self._waiting_to_complete = []
        self._data_received = {}
        self._connections = []
        self._running = True
        self._encoding = 'UTF-8'
        self._bytes_to_receive = 1024

        self._logger = Logger('Reactor' + str(reactor_num))

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger.debug('Socket created')

        self._bind_socket()

        # start listening on socket
        self._server.listen(5)
        self._connections.extend([self._server, sys.stdin])
        self._logger.info('Socket now listening')

    def _bind_socket(self):
        # bind socket to local host and port
        try:
            self._server.bind((self._host, self._port))
        except socket.error as msg:
            self._logger.error('Bind failed.')
            sys.exit()

        self._logger.debug('Socket bind complete')

    def _handle_new_connection(self):

        # wait to accept a connection - blocking call
        connection, addr = self._server.accept()

        # set the socket object to none blocking so it will not get our thread stuck
        connection.setblocking(0)
        self._connections.append(connection)
        self._logger.debug('Connected with ' + addr[0] + ':' + str(addr[1]))

        # sending message to connected client
        connection.send(bytes('Welcome to the server. Type something and hit enter\n', self._encoding))

    def _handle_new_message_received(self, connection):
        try:
            self._waiting_to_complete.remove(connection)
        except:
            pass

        # receiving from client
        try:
            data = connection.recv(self._bytes_to_receive)
        except:
            data = None

        if not data:
            reply = 'OK...'
            try:
                connection.send(bytes(reply, self._encoding))
                self._logger.info('Replied to client and removing it from our waiting list')
            except BrokenPipeError:
                connection.close()
                self._connections.remove(connection)
                self._logger.warn('Disconnected not clenaly from client')

        elif b'end' in data:
            connection.close()
            self._connections.remove(connection)
            self._logger.debug('Disconnected clenaly from client')

        else:
            self._logger.debug('Got new data from client, putting the client in our waiting list')
            self._waiting_to_complete.append(connection)
            if self._data_received.get(connection) is not None:
                self._data_received[connection] += data
            else:
                self._data_received[connection] = data

    def _handle_acceptable_object(self, acceptable_object):
        if acceptable_object == self._server:
            self._handle_new_connection()
        elif acceptable_object == sys.stdin:
            # handle standard input
            junk = sys.stdin.readline()
            # stop the server
            self._running = False
        else:
            self._handle_new_message_received(acceptable_object)

    def run(self):
        '''
        The heart of our async logic, process new connections, new messages from existing connections
        or complete reading the data from receiving messages
        '''
        next = 0
        try:
            while self._running:
                # dont wait at all, check and continue without blocking
                input_ready, output_ready, except_ready = select.select(self._connections, [], [], 0)

                # did we got anything from one of the file descriptors?
                # do we have anything waiting?
                if input_ready:
                    for acceptable_object in input_ready + self._waiting_to_complete:
                        self._handle_acceptable_object(acceptable_object)

                # we have nothing in the file descriptor, process one of the socket objects in the
                # waiting list and check again using the select
                elif self._waiting_to_complete:
                    if next >= len(self._waiting_to_complete):
                        next = 0
                    next_socket_object_to_handle = self._waiting_to_complete[next]
                    self._handle_acceptable_object(next_socket_object_to_handle)
                    next += 1

        except Exception as e:
            traceback.print_exc()

        finally:
            self._logger.info('Closing server')
            self._server.close()


r = Reactor('', 8889)
r.run()
