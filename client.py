import socket
import sys
import time
import base64

if len(sys.argv) != 4 :
    print("Usage: python client.py <server_host> <server_port> <file_list_path>")
    sys.exit(1)

server_host = sys.argv[1]
server_port = int(sys.argv[2])
file_list_path = sys.argv[3]

try:
    with open(file_list_path, 'r') as file_list:
        file_names = file_list.read().splitlines()
except FileNotFoundError:
    print(f"File list {file_list_path} not found.")
    sys.exit(1)

def send_udp(sock, server_addr, message, max_retries=5):
    retries = 0
    timeout = 1
    while retries < max_retries:
        try:
            #send
            sock.sendto(message.encode(), server_addr)
            # set
            sock.settimeout(timeout)
            # wait
            data, server = sock.recvfrom(4096) 
            return data.decode()
        except socket.timeout:
            # try again
            retries += 1
            timeout *= 2
            print(f"Timeout ({retries}/{max_retries}), retrying...")
    print("Max retries reached. Giving up.")
    return None

