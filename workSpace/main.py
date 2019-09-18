import time

import application
import application_executor
import http_application
import wifi

executor = application_executor.MicroPythonExecutor()


class CustomApplication(application.AbstractApplication):
    def __init__(self):
        super().__init__()
        self.__loop_times = 0

    def setup(self):
        print('set up')

    def loop(self):
        self.__loop_times += 1
        print('loop', self.__loop_times)
        time.sleep(0.5)


handler = http_application.StaticRequestHandler(executor, base_path='/')


class IndexController(http_application.Controller):
    def get(self, request):
        return 'OK' + request.method


index_controller = IndexController()
handler.register_handler('/', index_controller)


class PinController(http_application.Controller):
    def get(self, request):
        request.ctx.pin_out(1, 2)
        return 'OK'

    def post(self, request):
        body = request.body
        ctx = request.ctx
        print('PIN Request',body)
        if body == 'ON':
            ctx.pin_out(2, 1)
        elif body == 'OFF':
            ctx.pin_out(2, 0)
        else:
            return '400 BAD_REQUEST', 'Invalidate Params'
        return 'OK'


pin_controller = PinController()
handler.register_handler('/pin', pin_controller)


class NetApplication(http_application.AbstractHttpServerApplication):
    def __init__(self, host, port):
        super().__init__(handler, host, port)


def main():
    wifi.connect()
    apps = [CustomApplication(), NetApplication('0.0.0.0', 8081)]
    executor.run(apps)


if __name__ == '__main__':
    main()


