class AbstractApplication:
    def __init__(self):
        self.__executor = None

    def set_executor(self, executor):
        self.__executor = executor

    def get_executor(self):
        return self.__executor

    def setup(self):
        pass

    def loop(self):
        pass
