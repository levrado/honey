class Callback(object):
    def __init__(self, callbale):
        self._callable = callable

    def call(self, data):
        self._callable(data)
