import os
import re

import poll_socket_application

# 考虑到嵌入式设备的硬件性能，这里规定了每次Http请求包的最大大小
MAX_HTTP_REQUEST_SIZE = 1024


class ServerError(Exception):
    def __init__(self, err):
        super().__init__(err)


class RegisterError(Exception):
    def __init__(self, err):
        super().__init__(err)


class AbstractHttpServerApplication(poll_socket_application.AbstractPollerSocketApplication):
    def __init__(self, handler, host, port=80):
        super().__init__(host, port)
        self.__handler = handler

    def on_read_enable(self, socket_wrap):
        socket = socket_wrap.get_socket()
        data = socket.recv(MAX_HTTP_REQUEST_SIZE)
        method, url, headers, body = self.http_unpack(data)
        status, resp = self.__handler(url=url, headers=headers, body=body, method=method)
        socket.send(('HTTP/1.1 %s\r\n' % status).encode())
        socket.send(('Content-Length: %s\r\n' % len(resp)).encode())
        socket.send(b'\r\n')
        socket.send(resp.encode())
        socket_wrap.close()

    @staticmethod
    def http_unpack(data):
        lines = data.decode().split('\r\n')
        status_line = lines[0]
        method, url, version = AbstractHttpServerApplication.unpack_status_line(status_line)
        print('Resolve request [%s][%s][%s]' % (method, url, version))

        headers, line_num = AbstractHttpServerApplication.unpack_headers(lines[1::])
        if len(lines) > line_num + 2:
            body = ''.join(lines[line_num + 2::])
        else:
            body = None
        return method, url, headers, body

    @staticmethod
    def unpack_status_line(status_line):
        res = re.match(r'^(GET|POST|PUT|DELETE|OPTION)\s(.+)\s(.*)', status_line)
        method = res.group(1)
        url = res.group(2)
        try:
            version = res.group(3)
        except Exception as e:
            print(type(e))
            version = None
        return method, url, version

    @staticmethod
    def unpack_headers(lines):
        headers = {}
        line_num = 0
        for line in lines:
            if len(line) == 0:
                break
            line_num += 1
            name_and_value = line.split(':')
            item_len = len(name_and_value)
            if item_len == 2:
                header_name = name_and_value[0]
                header_value = name_and_value[1]
            elif item_len > 2:
                header_name = name_and_value[0]
                header_value = name_and_value[1::]
            elif item_len == 1:
                header_name = name_and_value[0]
                header_value = None
            else:
                continue
            headers[header_name] = header_value
        return headers, line_num


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


class AbstractRequestHandler:
    def __init__(self, ctx):
        self.__ctx = ctx
        self.__handlers = {}
        self.__middleware = {
            'before': [],
            'after': []
        }

    @property
    def ctx(self):
        return self.__ctx

    def register_handler(self, path, controller):
        if path in self.__handlers:
            raise RegisterError('Controller has been registered')
        if isinstance(controller, Controller):
            self.__handlers[path] = controller
        else:
            raise RegisterError('invalidate param controller')

    def use_before(self, fn):
        self.__middleware['before'].append(fn)

    def use_after(self, fn):
        self.__middleware['after'].append(fn)

    def __before_call(self, method, url, headers, body):
        for before_middleware in self.__middleware['before']:
            method, url, headers, body = before_middleware(method, url, headers, body)
        return method, url, headers, body

    def on_not_found(self, method, url, headers, body):
        return '404 NOT_FOUND', '<h1>Page Not Fount:%s</h1>%s' % (url, self)

    @staticmethod
    def __call_controller(controller, method, url, headers, body, ctx):
        request = Request(method, url, headers, body, ctx)
        if method == 'GET':
            return controller.get(request)
        elif method == 'POST':
            return controller.post(request)
        elif method == 'DELETE':
            return controller.delete(request)
        elif method == 'PUT':
            return controller.put(request)
        elif method == 'OPTION':
            return controller.option(request)
        else:
            return '405 METHOD_NOT_ALLOWED', 'Request method %s not allowed' % method

    def __call__(self, *args, **kwargs):
        method = kwargs['method']
        url = kwargs['url']
        headers = kwargs['headers']
        body = kwargs['body']
        method, url, headers, body = self.__before_call(method, url, headers, body)
        if '?' in url:
            real_url = url.split('?')[0]
        else:
            real_url = url
        if real_url not in self.__handlers:
            return self.on_not_found(method, url, headers, body)
        handler = self.__handlers[real_url]

        resp = AbstractRequestHandler.__call_controller(handler, method, url, headers, body, self.ctx)
        if isinstance(resp, str):
            return '200 OK', resp
        elif isinstance(resp, tuple):
            if not len(resp) == 2:
                raise ServerError('Invalidate response length: %s' % len(resp))
            return resp
        else:
            raise ServerError('Invalidate response type %s' % type(resp))


class StaticRequestHandler(AbstractRequestHandler):
    def __init__(self, ctx, base_path='/'):
        super().__init__(ctx)
        self.__base_path = base_path

    def on_not_found(self, method, url, headers, body):
        if '?' in url:
            url = url.split('/')[0]
        filename = self.__base_path + url
        if not os.path.exists(filename):
            return super().on_not_found(method, url, headers, body)
        print('Resolve Static request', filename)
        body = StaticRequestHandler.__read_file(filename)
        return '200 OK', body

    @staticmethod
    def __read_file(filename):
        f = open(filename)
        with f:
            content = f.read()
        return content
