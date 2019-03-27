#!/usr/bin/env python3

import argparse
import asyncore
import queue
import random
import socket
import threading


import shared


class socket_dispatcher(asyncore.dispatcher_with_send):
    def __init__(self, socket):
        super().__init__(socket)
        self._queue = queue.Queue()
        self._host, self._port = self.socket.getsockname()[0:2]

    def handle_close(self):
        print('Closed connection [{}]:{}'.format(self._host, self._port))
        self.close()

    def handle_read(self):
        bytes = self.recv(shared.BUFFER_SIZE)
        if not bytes:
            return

        self._queue.put(bytes)
        print('Received from [{}]:{}\n{}'.format(
            self._host, self._port, bytes.decode('utf-8')))

    def handle_write(self):
        data = self._queue.get()
        if data is None:
            return
        self.send(data)

    def writable(self):
        return not self._queue.empty()


class server_dispatcher(asyncore.dispatcher_with_send):
    def __init__(self, port: int, host: str, family: int):
        super().__init__()
        self.create_socket(family=family, type=socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(1)

        print("Bound to [{}]:{}".format(host, port))

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            return

        socket, remote = pair
        socket_dispatcher(socket)

        host, port = remote[0:2]
        print('Accepted connection from [{}]:{}'.format(host, port))


if __name__ == "__main__":
    # parse program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', default='localhost', type=str)
    random_port = random.choice(range(49152, 65535))  # rfc6335: dynamic ports
    parser.add_argument('-p', '--port', default=random_port, type=int)
    args = parser.parse_args()

    # resolve binding endpoints
    addrs = socket.getaddrinfo(args.host, args.port, type=socket.SOCK_DGRAM)
    for addr in addrs:
        family, _, _, _, endpoint = addr
        host, port = endpoint[0:2]
        # create server object
        server_dispatcher(port, host, family)

    # start io loop
    threading.Thread(target=lambda: asyncore.loop()).start()
