import socket
import struct

# Define the PLC's IP address
plc_ip = '192.168.1.100'

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

# Send the program upload request
request = struct.pack('>HHHHHH', 0x0003, 0x0000, rack, slot, 0x0000, 0x0000)
sock.send(request)

# Receive the program data
program_data = b''
while True:
    data = sock.recv(1024)
    if not data:
        break
    program_data += data

# Save the program data to a file
with open('program_data.txt', 'wb') as f:
    f.write(program_data)

# Close the socket
sock.close()