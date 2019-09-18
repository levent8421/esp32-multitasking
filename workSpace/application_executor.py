class Executor:
    def __init__(self):
        self.__apps = None
        self.__running_flag = True

    def run(self, apps):
        self.__apps = apps
        self.__setup_apps()
        while self.__running_flag:
            self.__do_loop()

    def __setup_apps(self):
        if not self.__apps:
            return
        for app in self.__apps:
            app.set_executor(self)
            app.setup()

    def __do_loop(self):
        if not self.__apps:
            return
        for app in self.__apps:
            try:
                app.loop()
            except Exception as e:
                print('Executor: Error on run application error=[%s], errorType=[%s]' % (e, type(e)))
                raise e
            if not self.__running_flag:
                return

    def stop(self):
        self.__running_flag = False


class MicroPythonExecutor(Executor):
    def __init__(self):
        super().__init__()
        self.__pin_cache = {}

    @staticmethod
    def build_pin(pin_no, mode):
        return 'PIN %s %s' % (pin_no, mode)

    def pin_out(self, pin_no, value):
        if pin_no in self.__pin_cache:
            pin = self.__pin_cache[pin_no]
        else:
            pin = MicroPythonExecutor.build_pin(pin_no, 1)
            self.__pin_cache[pin_no] = pin
        print(pin, pin_no, value)

