import logging


class Logger:

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
