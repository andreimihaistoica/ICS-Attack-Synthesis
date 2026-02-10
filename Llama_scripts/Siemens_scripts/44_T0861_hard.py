import socket
import struct
import sys

# Define the PLC's IP address range
ip_range = '192.168.1.0/24'

# Define the PLC's port number
port = 102

# Define the tag names and their corresponding addresses
tag_names = {
    'Fan_A': '%Q0.0',
    'Fan_B': '%Q0.1',
    'Fan_A_Red': '%Q0.4',
    'Fan_A_Green': '%Q0.5',
    'Fan_B_Red': '%Q0.2',
    'Fan_B_Green': '%Q0.3',
    'Motor_Temp': '%MW7',
    'Activate_Fan_A': '%M0.0',
    'Activate_Fan_B': '%M0.1',
    'Master_Fan_B_HMI': '%M0.5',
    'Motor_Status': '%M0.7',
    'Master_OFF': '%M0.6',
    'Overheating_Check': '%M0.2',
}

def find_plc_ip(ip_range):
    # Split the IP range into a list of IP addresses
    ip_addresses = ip_range.split('.')
    ip_addresses = [ip_addresses[0] + '.' + ip_addresses[1] + '.' + ip_addresses[2] + '.' + str(i) for i in range(1, 255)]

    # Scan each IP address to find the PLC
    for ip in ip_addresses:
        try:
            # Create a socket object
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the IP address and port
            sock.connect((ip, port))

            # Send a request to the PLC to get its IP address
            request = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01'
            sock.send(request)

            # Receive the response from the PLC
            response = sock.recv(1024)

            # Check if the response is valid
            if response[0] == 0x00 and response[1] == 0x00:
                return ip

            # Close the socket
            sock.close()
        except socket.error:
            pass

    # Return None if no PLC is found
    return None

def collect_tags(ip, tag_names):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC's IP address and port
    sock.connect((ip, port))

    # Send a request to the PLC to get the tag values
    request = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02'
    for tag in tag_names.values():
        request += tag.encode() + b'\x00'
    sock.send(request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Parse the response to get the tag values
    tag_values = {}
    for i, tag in enumerate(tag_names.keys()):
        value = struct.unpack('!H', response[(i * 2) + 2:(i * 2) + 4])[0]
        tag_values[tag] = value

    # Close the socket
    sock.close()

    # Return the tag values
    return tag_values

def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip(ip_range)

    # Check if the PLC's IP address is found
    if plc_ip:
        print(f'PLC IP address: {plc_ip}')

        # Collect the tag values
        tag_values = collect_tags(plc_ip, tag_names)

        # Print the tag values
        for tag, value in tag_values.items():
            print(f'{tag}: {value}')
    else:
        print('PLC not found')

if __name__ == '__main__':
    main()