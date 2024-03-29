import machine
from .board import MicroPythonBoardContext

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


class MicroPythonExecutor(Executor, MicroPythonBoardContext):
    def __init__(self):
        super().__init__()
        self.__pin_cache = {}
        self.__timer = machine.Timer(-1)
        self.__runner = self.__build_timer_runner()
        
    # 这里使用timer实现了application调度，是为了释放主程序，避免IDE识别不到开发板的情况发生
    def __build_timer_runner(self):
        def runner(t):
          self.__do_loop()
        return runner
    
    def run(self, apps):
        self.__apps = apps
        self.__setup_apps()
        self.__timer.init(period=100, mode=machine.Timer.PERIODIC, callback=self.__runner)
        



