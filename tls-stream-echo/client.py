#!/usr/bin/env python3

import argparse
import os
from os import path
import socket
import ssl
import threading


context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)


def send_thread(client: socket.socket):
    print('Enter the hello message, ends with EOF (e.g ^D):')
    while True:
        try:
            hello = input()
        except EOFError:
            hello = ''
        buffer = hello.encode('utf-8')

        client.send(bytes([len(buffer), ]))
        if (len(buffer) > 0):
            client.send(buffer)
        else:
            break


if __name__ == "__main__":
    # parse program arguments
    parser = argparse.ArgumentParser()
    # default to localhost
    parser.add_argument('-a', '--host', default='localhost', type=str)
    # default to random
    parser.add_argument('-p', '--port', required=True, type=int)
    # default to cert.pem
    parser.add_argument('-c', '--cert', default='cert.pem', type=str)
    args = parser.parse_args()

    cwd = os.getcwd()
    args.cert = path.join(cwd, args.cert)
    print('Local certificate: {}'.format(args.cert))

    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(args.cert)

    client = context.wrap_socket(socket.socket(), server_side=False)
    client.connect((args.host, args.port))
    host, port = client.getpeername()[0:2]
    print('Connected to [{}]:{}'.format(host, port))
    print('Remote certificate: {}'.format(client.getpeercert()))
    print('Cipher: {}'.format(client.cipher()))

    threading.Thread(target=send_thread, daemon=True,
                     kwargs={'client': client}).start()

    while True:
        size_buffer = client.recv(1)
        if len(size_buffer) == 0:
            break
        size = size_buffer[0]
        print('(pending {})'.format(size))

        buffer = bytes()
        while len(buffer) != size:
            buffer_size = min([64, size - len(buffer)])
            buffer = buffer + client.recv(buffer_size)
            # print('(pending {})'.format(size - len(buffer)))

        print('Response> {}'.format(buffer.decode('utf-8')))

    client.close()
