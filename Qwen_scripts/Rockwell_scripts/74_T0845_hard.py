import socket
import pycomm3
from pycomm3 import LogixDriver

def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
                if result == 0:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except socket.error:
            continue
    print("PLC not found in the specified subnet.")
    return None

def upload_program(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Read the program from the PLC
            program = plc.get_program()
            
            # Save the program to a file
            with open("plc_program.l5x", "w") as file:
                file.write(program)
            
            print(f"Program uploaded successfully from PLC at IP: {plc_ip}")
    except Exception as e:
        print(f"Error uploading program: {e}")

if __name__ == "__main__":
    # Discover the PLC IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Upload the program from the PLC
        upload_program(plc_ip)