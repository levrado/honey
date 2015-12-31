import socket
import select
import sys
import traceback
import logging

import protocols.tcp
import utils


class Reactor:

    def __init__(self):

        self._data_received = {}
        self._connections = []
        self._servers = {}
        self._clients = {}
        self._callbacks = []
        self._running = False

        self._logger = utils.Logger('Reactor')

    def _handle_new_connection(self, server):

        # wait to accept a connection - blocking call
        connection, addr = server.handle_connection_made()

        # set the socket object to none blocking so it will not get our thread stuck
        self._connections.append(connection)
        self._clients[connection] = server

    def _handle_new_message_received(self, connection):
        self._clients[connection].handle_data_received(connection)

    def _handle_acceptable_object(self, acceptable_object):
        if acceptable_object == sys.stdin:
            # handle standard input
            junk = sys.stdin.readline()
            # stop the server
            self._running = False
        elif self._servers.get(acceptable_object) is not None:
            self._handle_new_connection(self._servers.get(acceptable_object))
        else:
            self._handle_new_message_received(acceptable_object)

    def add_server(self, host, port, HandlerClass):
        tcp_server = protocols.tcp.Server(host, port, HandlerClass)
        self._servers[tcp_server.socket] = tcp_server
        self._connections.append(tcp_server.socket)

def _handle_io():
    select_connections_list = main_reactor._connections + [sys.stdin]
    # dont wait at all, check and continue without blocking
    # TODO make this a blocking stmnt, handle the existing connections on a new thread (sub process)
    input_ready, output_ready, except_ready = select.select(select_connections_list, [], [], 0)

    # did we got anything from one of the file descriptors?
    if input_ready:
        for acceptable_object in input_ready:
            main_reactor._handle_acceptable_object(acceptable_object)

def run():
    '''
    The heart of our async logic, process new connections, new messages from existing connections
    or complete reading the data from receiving messages
    '''
    main_reactor._running = True
    next = 0
    try:
        while main_reactor._running:
            '''
            Project Goals:

            Accept a set of file descriptors you are interested in performing I/O with.
            Tell you, repeatedly, when any file descriptors are ready for I/O.
            Provide lots of nice abstractions to help you use the reactor with the least amount of effort.
            Provide implementations of UDP and TCP protocols that you can use out of the box.

            '''
            _handle_io()
    except Exception as e:
        traceback.print_exc()

    finally:
        main_reactor._logger.info('Stoppin reactor')

def add_tcp_server(host, port, HandlerClass):
    main_reactor.add_server(host, port, HandlerClass)

main_reactor = Reactor()
