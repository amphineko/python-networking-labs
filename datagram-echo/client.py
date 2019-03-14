#!/usr/bin/env python3

import argparse
import asyncore
import random
import socket
import sys
import threading

import shared


class client_dispatcher(shared.dispatcher):
    _host: str
    _port: int

    def __init__(self, port: int, host: str, family: int):
        super().__init__(family)
        self._host = host
        self._port = port
        self.connect((port, host))

    def handle_connect(self):
        print('INFO: Connected to [{0}]:{1}'.format(self._host, self._port))

    def handle_read(self):
        bytes, address = self.socket.recvfrom(4096)
        port, host = address[0:2]  # slice unneeded members
        if port != self._port or host != self._host:
            print('WARN: Received with invalid remote address [{0}]:{1}'
                  .format(host, port))
            return
        print('INFO: Received from [{0}]:{1}\n{2}'.format(
            host, port, bytes.decode('utf-8')))


def read_keyboard(client: client_dispatcher):
    while True:
        line = sys.stdin.readline()
        if line is None:
            client.close()
        client.send(line.encode('utf-8'))  # FIXME: send async


if __name__ == "__main__":
    # parse program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    # resolve remote endpoint
    addr_list = socket.getaddrinfo(
        args.host, args.port, type=socket.SOCK_DGRAM)
    if len(addr_list) < 1:
        raise 'Cannot resolve the given hostname'

    # select remote endpoint, randomly
    family, _, _, _, endpoint = random.choice(addr_list)
    port, host = endpoint[0:2]

    # create client object
    client = client_dispatcher(port, host, family)

    # start io loop
    threading.Thread(target=lambda: asyncore.loop()).start()

    # start keyboard thread
    input_thread = threading.Thread(target=lambda: read_keyboard(client))
    input_thread.daemon = True
    input_thread.start()
