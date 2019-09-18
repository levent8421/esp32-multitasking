import select

import socket_application as sa

ALL_EVENT = select.POLLIN | select.POLLOUT | select.POLLERR
POLL_TIMEOUT = 100


class SocketWrap:
    def __init__(self, socket, app):
        self.__socket = socket
        self.__app = app

    def get_socket(self):
        return self.__socket

    def close(self):
        fd = self.__socket.fileno()
        self.__socket.close()
        self.__app.remove_socket(fd)


class AbstractPollerSocketApplication(sa.AbstractSocketServerApplication):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.__poller = None
        self.__socket_num = 0
        self.__fd_socket_table = {}

    def setup(self):
        super().setup()
        self.__poller = select.poll()

    def on_connected(self, conn, addr):
        self.__poller.register(conn, ALL_EVENT)
        self.__fd_socket_table[conn.fileno()] = conn
        self.__socket_num += 1

    def loop(self):
        super().loop()
        if self.__socket_num > 0:
            events = self.__poller.poll(POLL_TIMEOUT)
            if events and len(events):
                self.__read_poll_event(events)

    def __read_poll_event(self, events):
        for fd, flag in events:
            fd = fd.fileno()
            if fd not in self.__fd_socket_table:
                continue
            socket = self.__fd_socket_table[fd]
            socket_wrap = SocketWrap(socket, self)
            if flag & select.POLLIN:
                try:
                    self.on_read_enable(socket_wrap)
                except Exception as e:
                    self.remove_socket(fd)
                    print('Error on process socket, ', e)
                    raise e
            if flag & select.POLLHUP:
                self.remove_socket(fd)
                print('Socket closed, remove it', fd)
            if flag & select.POLLERR:
                self.remove_socket(fd)
                print('Socket Error, remove it', fd)

    def remove_socket(self, fd):
        if fd not in self.__fd_socket_table:
            return
        socket = self.__fd_socket_table[fd]
        self.__poller.unregister(socket)
        del self.__fd_socket_table[fd]
        self.__socket_num -= 1

    def on_read_enable(self, socket_wrap):
        pass

