from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import time

# Define network to scan (modify accordingly)
network_range = "192.168.1.0/24"

def find_plc_ip():
    print("[*] Scanning network to find PLC IP...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range), timeout=2, verbose=False)
    
    for send, receive in ans:
        # Check MAC address vendor (Modify for your PLC vendor if needed)
        if receive.hwsrc.startswith(("00:1A:C2", "00:0E:C6")):  # Example MAC vendor prefixes
            print(f"[+] Identified potential PLC at IP: {receive.psrc}")
            return receive.psrc
    
    print("[-] PLC not found on the network!")
    return None

def get_plc_mode(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)

    if not client.open():
        print("[-] Failed to connect to PLC!")
        return None

    # Assume the PLC stores the operation mode in holding register 0x0000 (Modify based on vendor documentation)
    reg_address = 0x0000
    mode_value = client.read_holding_registers(reg_address, 1)

    if mode_value:
        mode_value = mode_value[0]
        mode_dict = {
            0: "PROGRAM",
            1: "RUN",
            2: "REMOTE",
            3: "STOP",
            4: "RESET",
            5: "TEST/MONITOR"
        }
        mode_text = mode_dict.get(mode_value, "UNKNOWN")
        print(f"[+] PLC Operating Mode: {mode_text}")
        return mode_text
    else:
        print("[-] Unable to retrieve PLC mode.")

    client.close()

def main():
    plc_ip = find_plc_ip()
    
    if plc_ip:
        get_plc_mode(plc_ip)
    else:
        print("Exiting script.")

if __name__ == "__main__":
    main()