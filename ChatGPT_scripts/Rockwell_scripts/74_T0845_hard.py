from scapy.all import *
from pylogix import PLC
import time

# Function to discover Rockwell PLCs (Micro850) using EtherNet/IP
def discover_plc():
    print("[*] Scanning network for PLC...")

    # EtherNet/IP: List Identity Request (allows discovery)
    enip_discover = bytes.fromhex("63 00 00 00 03 00 01 00 00 00 00 00 00 00 00 00")

    # Send broadcast probe to discover PLC
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(enip_discover, ("255.255.255.255", 44818))

    sock.settimeout(3)
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if addr:
                print(f"[+] Found PLC at {addr[0]}")
                return addr[0]  # Return the detected IP
    except socket.timeout:
        print("[-] No PLC detected on network.")
        return None

# Function to attempt program upload from Micro850 PLC
def upload_program(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")

    plc = PLC()
    plc.IPAddress = plc_ip

    try:
        # Attempt to read controller information (may require access privileges)
        program_data = plc.Read("Program")

        if program_data.Status == "Success":
            print("[+] Successfully extracted program data.")
            # Save the program output
            with open("downloaded_program.L5X", "w") as file:
                file.write(program_data.Value)
            print("[+] Program uploaded and saved as 'downloaded_program.L5X'.")
        else:
            print("[-] Failed to extract program data.")

    except Exception as e:
        print(f"[-] Error communicating with the PLC: {e}")

    finally:
        plc.Close()


# Main execution
if __name__ == "__main__":
    plc_ip = discover_plc()

    if plc_ip:
        upload_program(plc_ip)
    else:
        print("[-] Could not find PLC IP. Exiting.")