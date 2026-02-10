import socket
import struct
import time
from pylogix import PLC

def find_plc_ip(network_prefix):
    """
    Scans the local network for active devices and tries to identify a PLC.
    This is a basic approach and may need adjustment depending on the network structure.
    """
    for i in range(1, 255):  # Scan 1-254 in the subnet
        ip = f"{network_prefix}.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Timeout to avoid long waits
            result = sock.connect_ex((ip, 44818))  # Rockwell used port 44818 for Ethernet/IP
            sock.close()
            
            if result == 0:
                print(f"Potential PLC found at {ip}")
                return ip
        except socket.error:
            continue
    
    return None

def modify_plc_logic(plc_ip):
    """
    Connects to the PLC and attempts to modify a tag.
    """
    with PLC() as comm:
        comm.IPAddress = plc_ip 
        
        try:
            # Read an existing tag
            tag = 'SomeExistingTag'  # Replace with an actual tag
            response = comm.Read(tag)
            
            if response.Status == 'Success':
                print(f"Read successful: {tag} = {response.Value}")

                # Modify the tag value (for example, flip a bit or change a state)
                new_value = 1 if response.Value == 0 else 0
                write_response = comm.Write(tag, new_value)

                if write_response.Status == 'Success':
                    print(f"Successfully modified '{tag}' to {new_value}")
                else:
                    print(f"Failed to modify '{tag}'")

            else:
                print("Failed to read tag.")

        except Exception as e:
            print(f"Error modifying PLC logic: {e}")

if __name__ == "__main__":
    subnet = "192.168.1"  # Modify based on the network range
    plc_ip = find_plc_ip(subnet)

    if plc_ip:
        print(f"Connecting to PLC at {plc_ip}...")
        modify_plc_logic(plc_ip)
    else:
        print("No PLCs found on the network.")