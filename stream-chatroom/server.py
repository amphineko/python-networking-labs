#!/usr/bin/env python3

import argparse
import random
from socket import getaddrinfo, socket, SOCK_STREAM
from threading import Thread, Lock
from typing import List, Callable

MAX_RECV_BUFFER_SIZE = 2 ** 6
LENGTH_HEADER_SIZE = 2

channels = list()  # type: List[socket]
channels_lock = Lock()


def dispatch(buf: bytes):
    # concat [buffer size, buffer]
    send_buf = int.to_bytes(len(buf), LENGTH_HEADER_SIZE, 'big', signed=False) + buf
    # send to all clients
    with channels_lock:
        try:
            for channel in channels:
                channel.send(send_buf)
        except ConnectionError:
            # simply skip failed clients
            pass


def read_socket_forever(sock: socket, on_message: Callable[[bytes, str, int], None]):
    remote_host, remote_port = sock.getpeername()[0:2]
    print('Connection to [{}]:{} established.'.format(remote_host, remote_port, ))

    try:
        with channels_lock:
            channels.append(sock)
        while True:
            # receive message length
            recv_size_buf = sock.recv(LENGTH_HEADER_SIZE)  # type: bytes
            if recv_size_buf is None or len(recv_size_buf) == 0:
                raise ConnectionAbortedError()  # channel closed
            recv_size = int.from_bytes(recv_size_buf, byteorder='big', signed=False)  # type: int

            # receive message content
            buf = sock.recv(min([recv_size, MAX_RECV_BUFFER_SIZE, ]))
            if buf is None or len(buf) == 0:
                raise ConnectionAbortedError()  # socket closed
            # receive remaining chunks
            while len(buf) != recv_size:
                chunk = sock.recv(min([recv_size - len(buf), MAX_RECV_BUFFER_SIZE, ]))
                if chunk is None or len(chunk) == 0:
                    raise ConnectionAbortedError()  # socket closed
                buf += chunk

            on_message(buf, remote_host, remote_port)
    except ConnectionAbortedError:
        print('Connection to [{}]:{} has been closed.'.format(remote_host, remote_port, ))
    except ConnectionResetError:
        print('Connection to [{}]:{} has been reset'.format(remote_host, remote_port, ))
    finally:
        with channels_lock:
            channels.remove(sock)


def handle_message(buf: bytes, remote_host: str, remote_port: int):
    print('<[{}]:{}> {}'.format(remote_host, remote_port, buf.decode('utf-8'), ))
    dispatch(buf)


def listen(port: int, host: str, family: int):
    server = socket(family, SOCK_STREAM)
    print('Listening on [{}]:{}.'.format(host, port, ))
    server.bind((host, port))
    server.listen(1)
    while True:
        channel = server.accept()[0]
        if channel is None:
            continue
        Thread(target=lambda: read_socket_forever(channel, handle_message), daemon=False).start()


def main():
    # parse program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', default='localhost', type=str)
    random_port = random.choice(range(49152, 65535))  # rfc6335: dynamic ports
    parser.add_argument('-p', '--port', default=random_port, type=int)
    args = parser.parse_args()

    # resolve binding endpoints
    bound_addresses = set()
    addresses = getaddrinfo(host=args.host, port=args.port)
    for address in addresses:
        family, _, _, _, endpoint = address
        host, port = endpoint[0:2]
        if host in bound_addresses:
            continue
        Thread(target=lambda: listen(port, host, family)).start()
        bound_addresses.add(host)


if __name__ == '__main__':
    main()
