import argparse
import os
from os import path
import socket
import ssl
import sys
import threading


context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)


def send_thread(client: socket.socket):
    print('Enter the hello message, ends with EOF (e.g ^D):')
    while True:
        try:
            hello = input()
        except EOFError:
            hello = '\0'
        buffer = hello.encode('utf-8')

        client.send(bytes([len(buffer), ]))
        client.send(buffer)


if __name__ == "__main__":
    # parse program arguments
    parser = argparse.ArgumentParser()
    # default to localhost
    parser.add_argument('-a', '--host', default='localhost', type=str)
    # default to random
    parser.add_argument('-p', '--port', type=int)
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
    print('Remote certificate: {}'.format(client.getpeercert()))
    print('Cipher: {}'.format(client.cipher()))

    threading.Thread(target=send_thread, daemon=True,
                     kwargs={'client': client}).start()

    while True:
        size_buffer = client.recv(1)
        if (len(size_buffer) == 0):
            break
        size = size_buffer[0]
        print('(pending {})'.format(size))

        buffer = bytes()
        while len(buffer) < size:
            buffer = buffer + client.recv(min([size - len(buffer), 64]))
            
        print('Response> {}'.format(buffer.decode('utf-8')))
