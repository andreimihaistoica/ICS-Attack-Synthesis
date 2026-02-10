import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with PLC(ip) as plc:
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to upload the program from the PLC
def upload_program(plc_ip):
    try:
        # Connect to the PLC
        with PLC(plc_ip) as plc:
            if plc.open():
                print(f"Connected to PLC at IP: {plc_ip}")
                
                # Upload the program
                program = plc.get_program()
                if program:
                    print("Program uploaded successfully.")
                    with open("plc_program.slc", "w") as file:
                        file.write(program)
                    print("Program saved to plc_program.slc")
                else:
                    print("Failed to upload the program.")
            else:
                print("Failed to connect to the PLC.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Upload the program from the PLC
        upload_program(plc_ip)

if __name__ == "__main__":
    main()