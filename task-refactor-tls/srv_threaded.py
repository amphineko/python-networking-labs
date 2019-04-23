#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter07/srv_threaded.py
# Using multiple threads to serve several clients in parallel.

# This version is modified to use TLS connections.

import zen_utils
from os import path
import ssl
from threading import Thread


def start_threads(listener, context, workers=4):
    t = (listener, context,)
    for _ in range(workers):
        Thread(target=zen_utils.accept_connections_forever, args=t).start()


if __name__ == '__main__':
    address, cert, key = zen_utils.parse_command_line('multi-threaded server')
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    print('Certificate: {}'.format(path.abspath(cert)))
    print('Key: {}'.format(path.abspath(key)))
    context.load_cert_chain(certfile=path.abspath(cert),
                            keyfile=path.abspath(key))
    listener = zen_utils.create_srv_socket(address)
    start_threads(listener, context)
