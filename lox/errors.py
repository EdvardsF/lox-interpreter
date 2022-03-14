class ParseError(Exception):
    pass


class RuntimeException(RuntimeError):
    def __init__(self, token, message):
        super(RuntimeException, self).__init__(message)
        self.message = message
        self.token = token