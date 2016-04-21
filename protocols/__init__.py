import abc


class Protocol:
    '''
    an abstract class for protocols
    '''
    __metadata__ = abc.ABCMeta

    def __init__(self):
        pass

    def handle_connection_made(self):
        '''
        this function is called when a connection is successful
        '''
        pass

    def handle_data_received(self, data):
        '''
        this function is called when there is a new data
        '''
        pass
