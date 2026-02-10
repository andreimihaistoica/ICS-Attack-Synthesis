import scapy.all as scapy
import psutil
import time

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the network range to scan
    network = "192.168.1.0/24"
    # Create an ARP request packet
    arp_request = scapy.ARP(pdst=network)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    # Send the packet and capture the response
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    # Filter the response to find the PLC
    for element in answered_list:
        print(f"IP: {element[1].psrc} - MAC: {element[1].hwsrc}")
        # Add your logic to identify the PLC based on MAC address or other criteria
        if element[1].hwsrc == "00:11:22:33:44:55":  # Example MAC address
            return element[1].psrc
    return None

# Function to monitor network traffic
def monitor_network_traffic(plc_ip):
    while True:
        # Get network connections
        connections = psutil.net_connections()
        for conn in connections:
            if conn.laddr.ip == plc_ip or conn.raddr.ip == plc_ip:
                print(f"Connection detected: {conn}")
        time.sleep(5)  # Check every 5 seconds

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        monitor_network_traffic(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()