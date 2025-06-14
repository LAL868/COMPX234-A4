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

def handle_client(client_address, file_name):
    # check if the file exists
    if not os.path.exists(file_name):
        err_msg = f"ERR {file_name} NOT_FOUND"
        server_socket.sendto(err_msg.encode(), client_address)
        return
    
    # select data transmission port
    data_port = None
    while data_port is None or data_port < 50000 or data_port > 51000:
        data_port = socket.htons(random.randint(0, 1000))  
        data_port = random.randint(50000, 51000)
    
    # create a data transmission socket
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(('0.0.0.0', data_port))  
    print(f"New data socket created on port {data_port} for {file_name}")
    
    # reply to OK message
    file_size = os.path.getsize(file_name)
    ok_msg = f"OK {file_name} SIZE {file_size} PORT {data_port}"
    server_socket.sendto(ok_msg.encode(), client_address)
    
    # handling FILE and CLOSE requests
    try:
        with open(file_name, 'rb') as file:
            while True:
                data, client = data_socket.recvfrom(4096)
                request = data.decode()
                request_parts = request.split()
                
                if request_parts[0] == "FILE" and request_parts[3] == "CLOSE":
                    close_ok_msg = f"FILE {file_name} CLOSE_OK"
                    data_socket.sendto(close_ok_msg.encode(), client)
                    print(f"Client closed {file_name}")
                    break

                if len(request_parts) >= 8 and request_parts[0] == "FILE" and request_parts[3] == "GET" and request_parts[4] == "START" and request_parts[6] == "END":
                    start = int(request_parts[5])
                    end = int(request_parts[7])
                    file.seek(start)
                    file_data = file.read(end - start + 1)  

                    encoded_data = base64.b64encode(file_data).decode()
                    response_msg = f"FILE {file_name} OK START {start} END {end} DATA {encoded_data}"
                    data_socket.sendto(response_msg.encode(), client)
                    print(f"Sent block {start}-{end} for {file_name}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        data_socket.close()