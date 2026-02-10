import socket
import ipaddress

def find_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1.0/24"
    
    # Create a socket to send a broadcast message
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)
    
    # Send a broadcast message to the subnet
    broadcast_message = b"DISCOVER"
    sock.sendto(broadcast_message, ('<broadcast>', 12345))
    
    # Listen for responses
    found_ips = []
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data == b"PLC":
                found_ips.append(addr[0])
        except socket.timeout:
            break
    
    return found_ips

# Example usage
plc_ips = find_plc_ip()
print("Found PLC IPs:", plc_ips)