#!/usr/bin/env python3

import argparse
import os
from os import path
import socket
import ssl
import threading


context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

GOODBYE = 'GOODBYE AND JOHN CEEEENAAAAAAAAAAA!'.encode('utf-8')


def send_john_cena(channel: socket.socket):
    channel.send(bytes([len(GOODBYE), ]) + GOODBYE)


def channel_thread(channel: socket.socket):
    host, port = channel.getpeername()[0:2]

    while True:
        size_buffer = channel.recv(1)
        if len(size_buffer) == 0:
            break
        size = size_buffer[0]
        print('(pending: {})'.format(size))

        if size == 0:
            print('Closing connection to [{}]:{}'.format(host, port))
            break

        buffer = bytes()
        while len(buffer) < size:
            buffer_size = min([size - len(buffer), 64])
            buffer = buffer + channel.recv(buffer_size)

        print('Received message from [{}]:{}.'.format(host, port))
        print(buffer.decode('utf-8'))

        channel.send(bytes([size, ]))
        channel.send(buffer)

    send_john_cena(channel)
    channel.shutdown(socket.SHUT_WR)
    channel.close()


def accept_thread(server: socket.socket):
    while True:
        channel, address = server.accept()
        host, port = address
        print('Accepted connection from [{}]:{}'.format(host, port))

        channel = context.wrap_socket(channel, server_side=True)
        channel.do_handshake()
        threading.Thread(target=channel_thread,
                         kwargs={'channel': channel}).start()


def create_server(port: int, host: str, family: int):
    server = socket.socket(family, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    return server


if __name__ == "__main__":
    # parse program arguments
    parser = argparse.ArgumentParser()
    # default to localhost
    parser.add_argument('-a', '--host', default='localhost', type=str)
    # default to random
    parser.add_argument('-p', '--port', default=0, type=int)
    # default to cert.pem
    parser.add_argument('-c', '--cert', default='cert.pem', type=str)
    # default to key.pem
    parser.add_argument('-k', '--key', default='key.pem', type=str)
    args = parser.parse_args()

    cwd = os.getcwd()
    args.cert = path.join(cwd, args.cert)
    print('Certificate: {}'.format(args.cert))
    args.key = path.join(cwd, args.key)
    print('Key: {}'.format(args.key))

    context.load_cert_chain(certfile=args.cert, keyfile=args.key)

    # resolve binding endpoints
    addrs = socket.getaddrinfo(args.host, args.port, type=socket.SOCK_DGRAM)
    for family, _, _, _, endpoint in addrs:
        host, port = endpoint[0:2]
        server = create_server(port, host, family)

        bind_host, bind_port = server.getsockname()[0:2]
        print('Listening at [{}]:{}'.format(bind_host, bind_port))

        threading.Thread(target=accept_thread, kwargs={
                         'server': server}).start()
