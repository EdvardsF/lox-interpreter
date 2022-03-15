class ParseError(Exception):
    pass


class RuntimeException(RuntimeError):
    def __init__(self, token, message):
        super(RuntimeException, self).__init__(message)
        self.message = message
        self.token = token


class Return(RuntimeError):
    def __init__(self, value):
        super(Return, self).__init__()
        self.value = value