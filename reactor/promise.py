import reactor


class Create:

    def __init__(self):
        self._callbacks = []

    def add_callback(self, func):
        self._callbacks.append(func)

    def fulfill(self, *args, **kwargs):
        reactor.add_fulfiller(self._callbacks.pop(), *args, **kwargs)

