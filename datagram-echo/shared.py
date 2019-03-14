import asyncore
import signal
import socket
import sys


class dispatcher(asyncore.dispatcher):
    def __init__(self, family: int):
        super().__init__()
        self.create_socket(family, socket.SOCK_DGRAM)

    def handle_close(self):
        self.close()

    def writable(self):
        return False
