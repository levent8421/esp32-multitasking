import time

import wifi

from mapp import StaticRequestHandler, \
    AbstractApplication, \
    MicroPythonExecutor, \
    Controller, \
    AbstractHttpServerApplication, \
    Response

executor = MicroPythonExecutor()


class CustomApplication(AbstractApplication):
    def __init__(self):
        super().__init__()
        self.__loop_times = 0

    def setup(self):
        print('set up')

    def loop(self):
        self.__loop_times += 1
        #print('loop', self.__loop_times)
        time.sleep(0.5)


handler = StaticRequestHandler(executor, base_path='/')


class IndexController(Controller):
    def get(self, request):
        return Response(headers=[('Location', '/index.html')], body='OK Index')


index_controller = IndexController()
handler.register_handler('/', index_controller)


class PinController(Controller):
    def get(self, request):
        request.ctx.pin_out(1, 2)
        return Response(body='OK Pin')

    def post(self, request):
        body = request.body
        ctx = request.ctx
        print('PIN Request', body)
        if body == 'ON':
            ctx.pin_out(2, 1)
        elif body == 'OFF':
            ctx.pin_out(2, 0)
        else:
            return Response(status=404, body='Invalidate Parameters')
        return Response(body='Pin operation OK')


pin_controller = PinController()
handler.register_handler('/pin', pin_controller)


class NetApplication(AbstractHttpServerApplication):
    def __init__(self, host, port):
        super().__init__(handler, host, port)
        
def on_wifi_ready():
    apps = [CustomApplication(), NetApplication('0.0.0.0', 8081)]
    executor.run(apps)

def main():
    wifi.connect(on_wifi_ready)
    


if __name__ == '__main__':
    main()



