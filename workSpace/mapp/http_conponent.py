from .http import ServiceError

METHOD_NOT_ALLOWED = ('405 METHOD_NOT_ALLOWED', 'Method not allowed')


class Controller:
    def get(self, request):
        return METHOD_NOT_ALLOWED

    def post(self, request):
        return METHOD_NOT_ALLOWED

    def delete(self, request):
        return METHOD_NOT_ALLOWED

    def put(self, request):
        return METHOD_NOT_ALLOWED

    def OPTION(self, request):
        return METHOD_NOT_ALLOWED


class Request:
    def __init__(self, method, path, headers, body, ctx):
        self.__method = method
        self.__path = path
        self.__headers = headers
        self.__body = body
        self.__ctx = ctx

    @property
    def method(self):
        return self.__method

    @property
    def path(self):
        return self.__path

    @property
    def headers(self):
        return self.__headers

    @property
    def body(self):
        return self.__body

    @property
    def ctx(self):
        return self.__ctx


HTTP_STATUS_TABLE = {
    200: b'200 OK',
    302: b'302 REDIRECT',
    400: b'400 BAD_REQUEST',
    404: b'404 NOT_FOUND',
    405: b'405 METHOD_NOT_ALLOWED',
    500: b'500 INTERNAL_SERVER_ERROR'
}


class Response:
    def __init__(self, status=200, headers=None, body=''):
        if status not in HTTP_STATUS_TABLE:
            raise ServiceError('Un support status code [%s]' % status)
        if isinstance(body, str):
            self.__body = body.encode()
        elif isinstance(body, bytes):
            self.__body = body
        else:
            raise ServiceError('Un support body type [%s]' % type(body))
        self.__status = status
        if headers:
            self.__headers = headers
        else:
            self.__headers = []

    @property
    def status_str(self):
        return HTTP_STATUS_TABLE[self.__status]

    @property
    def headers(self):
        return self.__headers

    @property
    def body(self):
        return self.__body

