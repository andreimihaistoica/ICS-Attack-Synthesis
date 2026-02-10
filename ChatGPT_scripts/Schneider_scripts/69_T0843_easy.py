import snap7
import socket
import struct
import os
import time

# Function to discover PLC(s) in the network
def find_plc():
    ip_range = "192.168.1."  # Modify this range to match the network
    found_ips = []

    for i in range(1, 255):  # Scan the entire subnet
        ip = f"{ip_range}{i}"
        try:
            client = snap7.client.Client()
            client.connect(ip, 0, 1)  # Assuming Rack: 0, Slot: 1 (Modify if needed)
            if client.get_connected():
                print(f"PLC found at {ip}")
                found_ips.append(ip)
                client.disconnect()
                return ip  # Returns the first found PLC
        except:
            pass  # If connection fails, move to the next IP

    if not found_ips:
        print("No PLCs found on the network.")
        return None

# Function to download a program to the PLC
def download_program(plc_ip):
    try:
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)
        
        if not client.get_connected():
            print(f"Failed to connect to PLC at {plc_ip}")
            return
        
        print(f"Connected to PLC at {plc_ip}. Initiating program download...")

        # Change the PLC mode to STOP before download (required for full download)
        client.plc_stop()
        time.sleep(2)  # Give the PLC time to stop

        # Load program file (Modify this path to match your PLC program file)
        program_file = "path/to/program_upload.s7p"

        if not os.path.exists(program_file):
            print("Program file not found!")
            return

        with open(program_file, "rb") as f:
            program_data = f.read()
        
        # Transmits the program (A realistic download procedure depends on PLC type)
        client.db_write(1, 0, program_data)  # Writing to a Data Block (example)

        print("Program successfully downloaded!")

        # Restart PLC
        client.plc_start()
        print("PLC restarted after upload.")

        client.disconnect()
    except Exception as e:
        print(f"Error during PLC program download: {e}")

# Main execution flow
if __name__ == "__main__":
    plc_ip = find_plc()
    
    if plc_ip:
        download_program(plc_ip)
    else:
        print("Could not locate a PLC on the network. Exiting.")