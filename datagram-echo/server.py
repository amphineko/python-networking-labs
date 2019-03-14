#!/usr/bin/env python3

import argparse
import asyncore
import random
import signal
import socket


class dispatcher(asyncore.dispatcher):
    def __init__(self, port: int, host: str, family: int):
        super().__init__()
        self.create_socket(family, socket.SOCK_DGRAM)
        self.bind((port, host))
        print('bound to [{0}]:{1}'.format(port, host))

    def handle_read(self):
        data, remote = self.socket.recvfrom(114514)
        host, port = remote[0:2]
        print('<[{0}]:{1}> {2}'.format(host, port, data.decode('utf-8')))
        self.socket.sendto(data, remote)

    def writable(self):
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', default='localhost', type=str)
    # dynamic ports range: rfc6335
    random_port = random.choice(range(49152, 65535))
    parser.add_argument('-p', '--port', default=random_port, type=int)
    args = parser.parse_args()

    addrs = socket.getaddrinfo(args.host, args.port, type=socket.SOCK_DGRAM)
    for addr in addrs:
        family, _, _, _, endpoint = addr
        port, host = endpoint[0:2]
        dispatcher(port, host, family)

    asyncore.loop()
