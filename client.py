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

# create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for file_name in file_names:

    download_msg = f"DOWNLOAD {file_name}"
    response = send_udp(client_socket, (server_host, server_port), download_msg)
    
    if response is None:
        print(f"Failed to download {file_name} (no response).")
        continue
    
    # analyze response
    response_parts = response.split()
    if response_parts[0] == "ERR":
        print(f"Server error: {response}")
        continue
    elif response_parts[0] == "OK":
        if len(response_parts) != 6 or response_parts[1] != file_name or response_parts[3] != "PORT":
            print(f"Invalid OK response: {response}")
            continue
        file_size = int(response_parts[2])
        data_port = int(response_parts[5])
        print(f"Downloading {file_name} (size: {file_size} bytes) via port {data_port}")
        
        # create
        with open(file_name, 'wb') as file:
            offset = 0
            block_size = 1000  # up to 1000 bytes per transmission
            while offset < file_size:
                start = offset
                end = min(offset + block_size, file_size) - 1
              
                file_msg = f"FILE {file_name} GET START {start} END {end}"
                data_response = send_udp(client_socket, (server_host, data_port), file_msg)
                
                if data_response is None:
                    print(f"Failed to get block {start}-{end} for {file_name}")
                    break
                
                # response to parsing data
                data_parts = data_response.split()
                if len(data_parts) < 8 or data_parts[0] != "FILE" or data_parts[1] != file_name or data_parts[2] != "OK":
                    print(f"Invalid data response: {data_response}")
                    continue
                
                encoded_data = " ".join(data_parts[7:])  
                decoded_data = base64.b64decode(encoded_data)
                
                # write file parsing data response
                file.seek(start)
                file.write(decoded_data)
                print("*", end="", flush=True)  
                
                offset = end + 1 
            
            if offset >= file_size:
                # send CLOSE request
                close_msg = f"FILE {file_name} CLOSE"
                close_response = send_udp(client_socket, (server_host, data_port), close_msg)
                
                if close_response and close_response.startswith("FILE " + file_name + " CLOSE_OK"):
                    print(f"\n{file_name} downloaded successfully!")
                else:
                    print(f"\nFailed to confirm close for {file_name}")
            else:
                print(f"\nDownload failed for {file_name} (incomplete)")

client_socket.close()