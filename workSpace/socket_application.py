import socket

import application


class AbstractSocketServerApplication(application.AbstractApplication):
    def __init__(self, host, port=80):
        super().__init__()
        self.__host = host
        self.__port = port
        self.__socket = None

    def setup(self):
        super().setup()
        self.__build_socket()

    def __build_socket(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind((self.__host, self.__port))
        self.__socket.setblocking(False)
        self.__socket.listen(1)

    def loop(self):
        try:
            conn, addr = self.__socket.accept()
        except OSError:
            return
        else:
            self.__on_accept_success(conn, addr)

    def __on_accept_success(self, conn, addr):
        try:
            self.on_connected(conn, addr)
        except Exception as e:
            print(type(e))

    def on_connected(self, conn, addr):
        pass

