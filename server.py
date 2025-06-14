import socket
import threading
import sys
import base64
import os

if len(sys.argv) != 2:
    print("Usage: python server.py <server_port>")
    sys.exit(1)

server_port = int(sys.argv[1])