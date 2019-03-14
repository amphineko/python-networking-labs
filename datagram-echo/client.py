#!/usr/bin/env python3

import argparse
import asyncore
import random
import socket
import sys
import threading


class dispatcher(asyncore.dispatcher):
    def __init__(self, port: int, host: str, family: int):
        super().__init__()
        self.create_socket(family, socket.SOCK_DGRAM)
        self.connect((port, host))
        print('connect to [{0}]:{1}'.format(host, port))
        self._host = host
        self._port = port

    def handle_read(self):
        data, addr = self.socket.recvfrom(114514)
        port, host = addr
        if port != self._port or host != self._host:
            print('DROPPED INVALID REMOTE [{0}]:{1}'.format(host, port))
        else:
            print('<[{0}]:{1}> {2}'.format(host, port, data.decode('utf-8')))

    def writable(self):
        return False


def read_keyboard(callback: dispatcher):
    while True:
        line = sys.stdin.readline()
        if line is None:
            asyncore.close_all()
        callback.send(line.encode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('address', type=str)
    args = parser.parse_args()

    addr_list = socket.getaddrinfo(
        args.address, args.port, type=socket.SOCK_DGRAM)
    if len(addr_list) < 1:
        raise 'Cannot resolve the given address'

    family, _, _, _, endpoint = random.choice(addr_list)
    port, host = endpoint[0:2]
    client = dispatcher(port, host, family)

    threading.Thread(target=lambda: read_keyboard(client)).start()
    asyncore.loop()
