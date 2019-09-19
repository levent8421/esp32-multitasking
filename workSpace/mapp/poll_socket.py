import select

from .socket_server import AbstractSocketServerApplication

ALL_EVENT = select.POLLIN | select.POLLOUT | select.POLLERR
POLL_TIMEOUT = 100


class SocketWrap:
    def __init__(self, socket, app):
        self.__socket = socket
        self.__app = app

    def get_socket(self):
        return self.__socket

    def close(self):
        self.__socket.close()
        self.__app.remove_socket(self.__socket)


class AbstractPollerSocketApplication(AbstractSocketServerApplication):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.__poller = None

    def setup(self):
        super().setup()
        self.__poller = select.poll()

    def on_connected(self, conn, addr):
        self.__poller.register(conn, ALL_EVENT)

    def loop(self):
        super().loop()
        events = self.__poller.poll(POLL_TIMEOUT)
        if events:
            self.__read_poll_event(events)

    def __read_poll_event(self, events):
        for socket, flag in events:
            socket_wrap = SocketWrap(socket, self)
            if flag & select.POLLIN:
                try:
                    self.on_read_enable(socket_wrap)
                except Exception as e:
                    self.remove_socket(socket)
                    print('Error on process socket, ', e)
                    raise e
            if flag & select.POLLHUP:
                self.remove_socket(socket)
                print('Socket closed, remove it', socket)
            if flag & select.POLLERR:
                self.remove_socket(socket)
                print('Socket Error, remove it', socket)

    def remove_socket(self, socket):
        self.__poller.unregister(socket)

    def on_read_enable(self, socket_wrap):
        pass
