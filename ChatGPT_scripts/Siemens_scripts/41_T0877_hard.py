import os
import snap7
from snap7.util import get_bool
import socket
import struct

# Function to discover the PLC's IP address using ARP scan (Linux/Windows)
def find_plc_ip():
    print("Scanning network for Siemens PLC...")
    
    # Run ARP scan to detect devices in the network (adjust interface as needed)
    arp_command = "arp -a"  # Windows/Linux compatible
    output = os.popen(arp_command).read()
    
    possible_ips = []
    
    for line in output.split('\n'):
        if "192.168." in line:  # Adjust for PLC subnet range
            ip = line.split()[0]
            possible_ips.append(ip)
    
    if not possible_ips:
        print("No possible PLCs found. Check network.")
        return None

    # Try connecting to the discovered IPs
    for ip in possible_ips:
        print(f"Trying IP: {ip}")
        client = snap7.client.Client()
        try:
            client.connect(ip, 0, 1)  # Rack=0, Slot=1 for S7-1200
            if client.get_connected():
                print(f"Connected to PLC at {ip}")
                return ip
        except:
            continue
        
    print("No Siemens PLC found.")
    return None

# Function to read I/O Image
def read_io_image(plc):
    try:
        # Read inputs (%I area)
        input_image = plc.read_area(snap7.types.Areas.PE, 0, 0, 10)  # Adjust size as per need (bytes)
        # Read outputs (%Q area)
        output_image = plc.read_area(snap7.types.Areas.PA, 0, 0, 10)  # Adjust size as per need (bytes)
        
        print("\n--- I/O Image ---")
        print(f"Inputs  (%I): {input_image}")
        print(f"Outputs (%Q): {output_image}")
        
        # Parsing specific I/O
        for byte_index in range(len(output_image)):
            for bit_index in range(8):
                io_status = get_bool(output_image, byte_index, bit_index)
                print(f"Q{byte_index}.{bit_index} Status: {io_status}")

    except Exception as e:
        print(f"Error reading I/O Image: {e}")

def main():
    plc_ip = find_plc_ip()
    if not plc_ip:
        return

    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, 0, 1)  # Rack=0, Slot=1 for S7-1200
        
        if plc.get_connected():
            print(f"Successfully connected to PLC at {plc_ip}")
            read_io_image(plc)
        
    except Exception as e:
        print(f"PLC Connection Error: {e}")
    
    finally:
        plc.disconnect()

if __name__ == "__main__":
    main()