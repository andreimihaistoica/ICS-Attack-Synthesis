import snap7
import struct
import socket
import subprocess

# Function to scan and detect Siemens PLC IP on the network
def get_plc_ip(network_prefix="192.168.1"):  # Change prefix for your network
    for last_octet in range(1, 255):
        ip = f"{network_prefix}.{last_octet}"
        try:
            # Using socket to test PLC port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)  # Set timeout for connection
            result = s.connect_ex((ip, 102))  # Port 102 is used by Siemens PLCs
            s.close()
            if result == 0:
                print(f"[+] PLC Found at: {ip}")
                return ip
        except:
            continue
    return None

# Function to connect to PLC
def connect_to_plc(ip):
    client = snap7.client.Client()
    try:
        client.connect(ip, 0, 1)  # Rack=0, Slot=1 for Siemens S7-1200
        if client.get_connected():
            print("[+] Connected to PLC!")
            return client
    except Exception as e:
        print(f"[-] Connection failed: {e}")
    return None

# Function to read memory (DB, Inputs, Outputs, etc.)
def read_tag_data(plc, address, size):
    try:
        data = plc.read_area(snap7.types.Areas.MK, 0, address, size)  # Read marker memory
        return struct.unpack(f"{size}B", data)
    except Exception as e:
        print(f"[-] Failed to read data at {address}: {e}")
        return None

# Main execution
def main():
    print("[*] Scanning Network for PLC...")
    plc_ip = get_plc_ip()

    if not plc_ip:
        print("[-] No PLC found! Exiting.")
        return

    plc = connect_to_plc(plc_ip)
    
    if not plc:
        print("[-] Unable to establish connection with PLC.")
        return

    print("[*] Collecting Tags and Points...")

    # Addresses defined in provided table
    tags = {
        "Fan_A": 0,
        "Fan_B": 1,
        "Fan_A_Red": 4,
        "Fan_A_Green": 5,
        "Fan_B_Red": 2,
        "Fan_B_Green": 3,
        "Motor_Temp": 7,  # INT variable
        "Activate_Fan_A": 0,
        "Activate_Fan_B": 1,
        "Overheating_Check": 2, 
        "Master_Fan_B_HMI": 5,
        "Motor_Status": 7
    }

    collected_data = {}
    for tag, address in tags.items():
        if tag == "Motor_Temp":  # INT-type data
            data = read_tag_data(plc, address, 2)  # Read 2 bytes for INT
            value = int.from_bytes(data, byteorder='big')
        else:
            data = read_tag_data(plc, address, 1)  # Read 1 byte for BOOL

            # Extracting single bit value
            if data:
                value = (data[0] & (1 << (address % 8))) >> (address % 8)
            else:
                value = None

        collected_data[tag] = value
        print(f"[+] {tag}: {value}")

    print("\n[*] Collection Complete. Data extracted.")

    return collected_data  # Could be sent to another system for analysis

if __name__ == "__main__":
    main()