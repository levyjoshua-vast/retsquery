

class RETSQueryException(Exception):
    
    def __init__(self, message):
        self._message = message
    
    @property
    def message(self):
        return self._message
    
    @message.setter
    def message(self, message): 
        self._message = message
