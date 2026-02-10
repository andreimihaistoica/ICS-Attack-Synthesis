import socket
import struct
import subprocess

# Define the network range to scan
network_range = '192.168.1.0/24'

# Use Nmap to scan the network and find the PLC's IP address
output = subprocess.check_output(['nmap', '-sT', network_range])

# Parse the output to find the PLC's IP address
for line in output.decode('utf-8').splitlines():
    if 'S7-1200' in line:
        plc_ip = line.split()[0]
        break

# Define the S7-1200 PLC's rack and slot numbers
rack = 0
slot = 1

# Define the program to be downloaded
program = b'...your_program_data_here...'

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the PLC
sock.connect((plc_ip, 102))

# Send the S7CommPlus protocol header
header = struct.pack('>HHHHHH', 0x0001, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000)
sock.send(header)

# Send the program download request
request = struct.pack('>HHHHHH', 0x0002, 0x0000, rack, slot, 0x0000, len(program))
sock.send(request)

# Send the program data
sock.send(program)

# Receive the response
response = sock.recv(1024)

# Check if the download was successful
if response[0] == 0x02 and response[1] == 0x00:
    print('Program downloaded successfully')
else:
    print('Error downloading program')

# Close the socket
sock.close()