import os

from .http import ServerError,ServiceError
from .http_conponent import Controller, Request, Response


class RegisterError(Exception):
    def __init__(self, err):
        super().__init__(err)


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
        return Response(status=404, body='Page [%s] not found!' % url)

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
            return Response(status=405, body='Method [%s] not allowed!')

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
            return Response(body=resp)
        elif isinstance(resp, Response):
            return resp
        else:
            raise ServiceError('Un support response type [%s]' % type(resp))


class StaticRequestHandler(AbstractRequestHandler):
    def __init__(self, ctx, base_path='/'):
        super().__init__(ctx)
        self.__base_path = base_path

    def on_not_found(self, method, url, headers, body):
        if '?' in url:
            url = url.split('/')[0]
        filename = self.__base_path + url
        if not StaticRequestHandler.__file_exists(filename):
            return super().on_not_found(method, url, headers, body)
        print('Resolve Static request', filename)
        body = StaticRequestHandler.__read_file(filename)
        return Response(body=body)

    @staticmethod
    def __read_file(filename):
        f = open(filename)
        with f:
            content = f.read()
        return content

    @staticmethod
    def __file_exists(filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False


