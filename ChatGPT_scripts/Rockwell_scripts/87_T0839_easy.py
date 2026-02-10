import os
import time
import socket
from scapy.all import ARP, Ether, srp

# Function to perform network scanning and locate the PLC's IP address
def scan_network(network_range):
    print(f"Scanning the network range: {network_range}")
    arp = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=0)[0]
    
    ip_list = []
    for sent, received in result:
        ip_list.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    return ip_list

# Function to simulate sending malicious firmware to the target PLC
def send_malicious_firmware(plc_ip, firmware_data="malicious_payload.bin"):
    print(f"Target PLC IP address: {plc_ip}")
    print("Simulating malicious firmware upload...")
    time.sleep(2)
    # Simulated firmware update logic (educational purpose)
    print(f"Uploading malicious firmware from {firmware_data} to {plc_ip}...")
    time.sleep(3)
    print(f"Firmware upload to {plc_ip} complete. Simulation ends here!")

# Function to demonstrate attack methods (educational purpose only)
def demonstrate_attack_methods(plc_ip):
    print(f"Simulated attack methods against IP {plc_ip}:")
    time.sleep(1)
    print("* Delayed Attack - Set a trigger time for the malicious action.")
    time.sleep(1)
    print("* Bricking the Ethernet Card - Simulate permanent damage.")
    time.sleep(1)
    print("* Random Attack or Failure - Randomize downtime events.")
    time.sleep(1)
    print("* Field Device Worm - Propagate malicious firmware to similar devices.")
    time.sleep(1)
    print("* Attacking Other Modules - Target other modular hardware.")
    print(f"Note: These actions are for educational purposes only!")

# Main simulation logic
if __name__ == "__main__":
    try:
        # Define the network range to scan
        network_range = "192.168.1.0/24"  # Adjust this according to your own simulated network

        print("Scanning the network for the PLC...")
        devices = scan_network(network_range)

        if not devices:
            print("No devices found on the network.")
            exit()

        print("\nDiscovered devices:")
        for device in devices:
            print(f"IP: {device['ip']}, MAC: {device['mac']}")

        # Assuming the first device is the PLC for this simulation
        plc_ip = devices[0]['ip']
        print(f"\nSimulating attack on target PLC with IP: {plc_ip}")

        # Send malicious firmware to the target PLC
        send_malicious_firmware(plc_ip)

        # Demonstrate simulated attack methods
        demonstrate_attack_methods(plc_ip)

    except KeyboardInterrupt:
        print("\nSimulation interrupted. Exiting.")
    except Exception as e:
        print(f"An error occurred: {e}")