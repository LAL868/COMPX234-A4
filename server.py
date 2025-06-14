import socket
import threading
import sys
import base64
import os

#resolve port number
if len(sys.argv) != 2:
    print("Usage: python server.py <server_port>")
    sys.exit(1)

server_port = int(sys.argv[1])

# create a primary UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', server_port))  
print(f"Server started on port {server_port}. Waiting for requests...")