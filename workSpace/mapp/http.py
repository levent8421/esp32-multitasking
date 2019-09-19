import re

from .poll_socket import AbstractPollerSocketApplication

# 考虑到嵌入式设备的硬件性能，这里规定了每次Http请求包的最大大小
MAX_HTTP_REQUEST_SIZE = 1024


class ServerError(Exception):
    def __init__(self, err):
        super().__init__(err)


class ServiceError(Exception):
    def __init__(self, err):
        super().__init__(err)


class AbstractHttpServerApplication(AbstractPollerSocketApplication):
    def __init__(self, handler, host, port=80):
        super().__init__(host, port)
        self.__handler = handler

    @staticmethod
    def __write_headers(socket, headers):
        for header in headers:
            socket.send(('%s: %s\r\n' % (header[0],header[1])).encode())

    def on_read_enable(self, socket_wrap):
        socket = socket_wrap.get_socket()
        data = socket.recv(MAX_HTTP_REQUEST_SIZE)
        try:
            method, url, headers, body = self.http_unpack(data)
            resp = self.__handler(url=url, headers=headers, body=body, method=method)
            status_line = resp.status_str
            body = resp.body
            socket.send(b'HTTP/1.1 ')
            socket.send(status_line)
            socket.send(('\r\nContent-Length: %s\r\n' % len(resp.body)).encode())
            AbstractHttpServerApplication.__write_headers(socket, resp.headers)
            socket.send(b'\r\n')
            socket.send(body)
        except ServerError as e:
            socket.send(b'HTTP/1.1 500 INTERNAL_SERVER_ERROR\r\n\r\n')
            socket.send(str(e).encode())
        finally:
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
        if not res:
            raise ServerError('Invalidate status line [%s]' % status_line)
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

