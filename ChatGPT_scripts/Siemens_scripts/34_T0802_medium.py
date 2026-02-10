import snap7
from snap7.util import get_string
from scapy.all import ARP, Ether, srp
import socket

# Helper function to scan for the Siemens PLC device
def find_plc_ip(network="192.168.0.1/24"):
    print("[*] Scanning for Siemens S7-1200 PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network), timeout=2, verbose=False)
    
    for snd, rcv in ans:
        if rcv.psrc.startswith("192.168.0."):  # Modify the subnet accordingly
            print(f"[+] Possible PLC detected at: {rcv.psrc}")
            return rcv.psrc  
    print("[-] No PLC found.")
    return None

# Function to collect PLC system information
def collect_plc_info(plc_ip):
    try:
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)  # Connect using Rack=0, Slot=1 for S7-1200

        if client.get_connected():
            print("[+] Successfully connected to PLC")

            # Get the CPU information
            plc_order_code = client.get_cpu_info()
            module_name = client.get_cpu_module_type()
            plc_type = client.get_cpu_type()
            serial_number = client.get_pdu_length()

            # Print the collected information
            print(f"[*] PLC IP: {plc_ip}")
            print(f"[*] PLC Type: {plc_type}")
            print(f"[*] CPU Model: {module_name}")
            print(f"[*] Order Code: {plc_order_code}")
            print(f"[*] Serial Number: {serial_number}")

            # Disconnect
            client.disconnect()
        else:
            print("[-] Unable to connect to PLC.")

    except Exception as e:
        print(f"[-] Error communicating with the PLC: {e}")

if __name__ == "__main__":
    # Step 1: Detect the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Collect and display PLC information
        collect_plc_info(plc_ip)
    else:
        print("[-] Could not determine PLC IP. Exiting.")