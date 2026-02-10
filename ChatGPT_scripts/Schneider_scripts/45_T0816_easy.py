from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import time

# Network Configuration
SUBNET = "192.168.1.0/24"  # Adjust this to your network range

# Function to scan the network and find the PLC's IP address
def discover_plc():
    print("[*] Scanning network to find PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=SUBNET), timeout=2, verbose=False)
    
    for _, recv in ans:
        ip = recv.psrc
        print(f"[+] Device found: {ip}")
        # Assume the first Modbus-enabled device is the PLC
        if is_modbus_device(ip):
            print(f"[+] PLC identified at: {ip}")
            return ip

    print("[-] No PLC found on the network.")
    return None

# Function to check if a device responds on the Modbus port (502)
def is_modbus_device(ip):
    client = ModbusTcpClient(ip)
    try:
        if client.connect():
            client.close()
            return True
    except:
        return False
    return False

# Function to restart the PLC (Modbus-based method)
def restart_plc(ip):
    client = ModbusTcpClient(ip)
    
    if not client.connect():
        print("[-] Failed to connect to PLC.")
        return

    print(f"[+] Connected to PLC at {ip}. Sending restart command...")
    
    # Writing to a control register to restart (assuming register 0x1000 triggers restart)
    try:
        client.write_register(0x1000, 1, unit=1)  # Modify register address as needed
        print("[+] Restart command sent successfully.")
    except Exception as e:
        print(f"[-] Failed to send restart command: {e}")

    client.close()

# Main Execution
if __name__ == "__main__":
    plc_ip = discover_plc()
    
    if plc_ip:
        restart_plc(plc_ip)
    else:
        print("[-] Unable to find PLC, terminating script.")