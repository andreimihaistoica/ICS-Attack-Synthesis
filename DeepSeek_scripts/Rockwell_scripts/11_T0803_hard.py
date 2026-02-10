import socket
import time
import subprocess
import re

# Function to find the PLC's IP address dynamically
def find_plc_ip():
    # Example: Use ARP or network scanning to find the PLC's IP
    # This is a placeholder for actual implementation
    arp_output = subprocess.check_output(["arp", "-a"]).decode()
    ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    ips = ip_pattern.findall(arp_output)
    
    # Assume the PLC's IP is in the list of discovered IPs
    # You may need to refine this logic based on your network
    for ip in ips:
        if ip.startswith("192.168"):  # Example: Filter for a specific subnet
            return ip
    return None

# Function to block command messages
def block_command_messages(plc_ip):
    # Create a raw socket to intercept packets
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.bind((plc_ip, 0))  # Bind to the PLC's IP and any port
    except Exception as e:
        print(f"Error creating socket: {e}")
        return

    print(f"Blocking command messages to PLC at {plc_ip}...")
    while True:
        try:
            packet, _ = s.recvfrom(65565)  # Receive packets
            # Filter out command messages (e.g., based on payload or port)
            # Example: Drop packets with specific content or destination port
            if b"command" in packet.lower():  # Example condition
                print("Command message blocked!")
                continue  # Drop the packet
            # Forward non-command messages (optional)
            # s.sendto(packet, (plc_ip, destination_port))
        except KeyboardInterrupt:
            print("Stopping block command message script.")
            break
        except Exception as e:
            print(f"Error: {e}")

# Main script
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        block_command_messages(plc_ip)
    else:
        print("Could not find PLC's IP address.")