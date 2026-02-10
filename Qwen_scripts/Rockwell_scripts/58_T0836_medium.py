import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the IP address of the PLC
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
    print("PLC not found on the network.")
    return None

# Function to modify a parameter in the PLC
def modify_plc_parameter(plc_ip, tag_name, new_value):
    try:
        with LogixDriver(plc_ip) as plc:
            # Read the current value of the tag
            current_value = plc.read(tag_name)
            print(f"Current value of {tag_name}: {current_value.value}")
            
            # Write the new value to the tag
            plc.write((tag_name, new_value))
            print(f"New value of {tag_name}: {new_value}")
    except Exception as e:
        print(f"Error modifying parameter: {e}")

# Main function
def main():
    # Discover the PLC IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Define the tag name and the new value to write
        tag_name = "MotorRunTime"  # Example tag name
        new_value = 600  # Example new value (e.g., run the motor for 600 seconds)
        
        # Modify the parameter
        modify_plc_parameter(plc_ip, tag_name, new_value)

if __name__ == "__main__":
    main()