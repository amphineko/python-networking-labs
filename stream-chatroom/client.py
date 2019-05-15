#!/usr/bin/env python3

import argparse
from builtins import input
from socket import getaddrinfo, socket, SOCK_STREAM
from threading import Thread

from server import read_socket_forever


def send_line(sock: socket, line: str):
    buf = line.encode('utf-8')
    # TODO: check buffer overflow (longer than 2 bytes)
    sock.send(len(buf).to_bytes(2, byteorder='big', signed=False) + buf)


def read_keyboard(sock: socket, username: str):
    while True:
        line = '[{}] {}'.format(username, input())
        if line is None:  # close on EOL
            sock.close()
        send_line(sock, line)


def handle_message(buf: bytes, remote_host, remote_port):
    print(buf.decode('utf-8'))


def main():
    # parse program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    # resolve remote endpoint
    addresses = getaddrinfo(args.host, args.port)
    if len(addresses) < 1:
        raise ConnectionError('Cannot resolve the given hostname')
    family, _, _, _, endpoint = addresses[0]
    host, port = endpoint[0:2]

    username = input('Username: ')

    sock = socket(family, SOCK_STREAM)
    sock.connect((host, port))
    print('Connected to [{}]:{}'.format(host, port, ))

    send_line(sock, '[{}] Joined.'.format(username, ))

    # start keyboard thread
    Thread(target=lambda: read_keyboard(sock, username), daemon=True).start()

    # read from socket
    Thread(target=lambda: read_socket_forever(sock, handle_message), daemon=False).start()


if __name__ == "__main__":
    main()
