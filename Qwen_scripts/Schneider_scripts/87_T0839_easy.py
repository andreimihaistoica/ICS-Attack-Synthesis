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
        # Add additional logic to identify the PLC based on MAC address or other criteria

# Function to monitor network traffic
def monitor_network_traffic():
    while True:
        # Get a list of all network connections
        connections = psutil.net_connections()
        for conn in connections:
            if conn.status == psutil.CONN_ESTABLISHED:
                print(f"Local Address: {conn.laddr} - Remote Address: {conn.raddr} - Status: {conn.status}")
        time.sleep(5)  # Check every 5 seconds

# Main function
def main():
    print("Discovering PLC IP address...")
    discover_plc_ip()
    print("Monitoring network traffic...")
    monitor_network_traffic()

if __name__ == "__main__":
    main()