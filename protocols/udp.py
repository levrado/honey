import protocols


class _Protocol(protocols.Protocol):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class Server(_Protocol):

    def __init__(self, port):

        s.bind(('', port))
