import snap7
import socket
import struct

def find_plc_ip():
    """Discovers the PLC IP within the local network by sending a broadcast request."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # S7 Discovery broadcast message 
    discovery_msg = b"\x03\x00\x00\x16\x11\xe0\x00\x00\x00\x00\x00\x01\x00\xc1\x02\x10\x02\xc2\x02\x03\x03\xc0\x01\x0a"
    udp_socket.sendto(discovery_msg, ('255.255.255.255', 102))
    
    udp_socket.settimeout(3)
    try:
        data, addr = udp_socket.recvfrom(1024)
        plc_ip = addr[0]  # Extract PLC IP from response
        return plc_ip
    except socket.timeout:
        print("PLC discovery timeout. Ensure PLC is reachable.")
        return None
    finally:
        udp_socket.close()

def modify_plc_parameter(plc_ip, db_number, byte_offset, new_value):
    """Modifies a control parameter on Siemens S7-1200 PLC."""
    plc = snap7.client.Client()
    
    try:
        # Connect to the PLC
        plc.connect(plc_ip, 0, 1)  # Rack=0, Slot=1 for S7-1200
        
        # Read the current data block
        data = plc.db_read(db_number, byte_offset, 4)  # Read 4 bytes (one float/dword)
        
        # Convert float to byte array
        new_value_bytes = struct.pack(">f", new_value)  # Convert float to 4-byte representation in big endian
        
        # Overwrite the specific parameter with the new value
        data = new_value_bytes  # Modify only the necessary bytes
        
        # Write modified data back to PLC
        plc.db_write(db_number, byte_offset, data)
        print(f"Successfully modified parameter at DB{db_number}, Offset: {byte_offset} to {new_value}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        plc.disconnect()

if __name__ == "__main__":
    print("Discovering PLC IP...")
    plc_ip = find_plc_ip()
    
    if plc_ip:
        print(f"PLC found at {plc_ip}")
        
        # Modify a critical process parameter (example: motor runtime limit)
        DB_NUMBER = 1        # Adjust as per actual DB number
        BYTE_OFFSET = 0      # Adjust based on the parameter's location
        NEW_VALUE = 120.0    # Example: Change motor runtime to 120 seconds
        
        modify_plc_parameter(plc_ip, DB_NUMBER, BYTE_OFFSET, NEW_VALUE)
    else:
        print("Could not find PLC. Exiting.")