#!/usr/bin/env python3

import argparse
import asyncore
import queue
import random
import socket
import sys
import threading

import shared


class client_dispatcher(asyncore.dispatcher_with_send):
    def __init__(self, port: int, host: str, family: int):
        super().__init__()
        self.create_socket(family=family, type=socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_close(self):
        print('Connection closed')
        self.close()

    def handle_connect(self):
        (self._host, self._port) = self.socket.getpeername()[0:2]
        print('Connected to [{}]:{}'.format(self._host, self._port))

    def handle_read(self):
        bytes = self.recv(shared.BUFFER_SIZE)
        if bytes is None:
            self.close()
            return
        print('Received from [{}]:{}\n{}'.format(
            self._host, self._port, bytes.decode('utf-8')))


def read_keyboard(client: client_dispatcher):
    while True:
        line = sys.stdin.readline()
        if line is None:  # close on EOL
            client.close()
        while not client.connected:  # block until socket connected
            pass
        client.send(line.encode('utf-8'))


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
    host, port = endpoint[0:2]

    # create client object
    client = client_dispatcher(port, host, family)

    # start io loop
    threading.Thread(target=lambda: asyncore.loop()).start()

    # start keyboard thread
    input_thread = threading.Thread(target=lambda: read_keyboard(client))
    input_thread.daemon = True
    input_thread.start()
