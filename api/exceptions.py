class ZabbixException(Exception):
    code = None

    def __init__(self, code: int, message: str, data: str):
        self.code = code
        self.message = message
        self.data = data

        super(ZabbixException, self).__init__(f'{data} {code}')


class MethodNotFound(ZabbixException):
    code = -32601

    def __init__(self, data: str):
        super(MethodNotFound, self).__init__(self.code, 'Method not found', data)


class InvalidParams(ZabbixException):
    code = -32602

    def __init__(self, data: str):
        super(InvalidParams, self).__init__(self.code, 'Invalid params', data)


class ZabbixExceptionFactory:
    def __init__(self, code: int):
        self.code = code

    def exception(self):
        for exc in ZabbixException.__subclasses__():
            if exc.code == self.code:
                return exc
