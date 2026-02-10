import socket
import struct
import time
from scapy.all import sniff, IP, TCP

# Configuration
PLC_IP = None
PLC_PORT = 502  # Common Modbus TCP port
MONITOR_INTERVAL = 10  # Time interval to check for rogue masters (in seconds)

# Function to find the PLC's IP address
def find_plc_ip():
    # This is a simple example. In a real scenario, you might use network scanning tools.
    # For this example, we'll assume the PLC is on the same subnet and use a simple broadcast.
    broadcast_ip = "255.255.255.255"
    port = 502  # Modbus TCP port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b"Who is the PLC?", (broadcast_ip, port))

    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found.")
        return None

# Function to monitor network traffic for rogue masters
def monitor_network():
    def packet_callback(packet):
        if packet.haslayer(IP) and packet.haslayer(TCP):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport

            if dst_ip == PLC_IP and dst_port == PLC_PORT:
                print(f"Detected communication to PLC: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
                if src_ip != "authorized_master_ip":  # Replace with the actual authorized master IP
                    print(f"Warning: Rogue master detected: {src_ip}")

    sniff(filter=f"tcp and port {PLC_PORT}", prn=packet_callback, store=0)

# Main function
def main():
    global PLC_IP
    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("PLC IP not found. Exiting.")
            return

    print(f"Monitoring network for rogue masters targeting PLC at {PLC_IP}:{PLC_PORT}")
    while True:
        monitor_network()
        time.sleep(MONITOR_INTERVAL)

if __name__ == "__main__":
    main()