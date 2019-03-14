#!/usr/bin/env python3

import argparse
import asyncore
import random
import socket
import threading

import shared


class server_dispatcher(shared.dispatcher):
    def __init__(self, port: int, host: str, family: int):
        # create socket
        super().__init__(family)
        # bind
        self.bind((host, port))
        print('INFO: Bound to [{0}]:{1}'.format(host, port))

    def handle_read(self):
        # async receive
        bytes, address = self.socket.recvfrom(4096)
        port, host = address[0:2]  # slice unneeded members
        print('INFO: Received from [{0}]:{1}\n{2}'.format(
            host, port, bytes.decode('utf-8')))
        # echo reply
        self.socket.sendto(bytes, address)  # FIXME: send async


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
