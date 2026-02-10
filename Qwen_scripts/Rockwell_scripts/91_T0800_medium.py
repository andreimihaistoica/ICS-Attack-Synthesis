import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet and range to scan
    subnet = '192.168.1.'
    start_ip = 1
    end_ip = 254

    for i in range(start_ip, end_ip + 1):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with LogixDriver(ip) as plc:
                if plc.info:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue

    print("PLC not found in the specified range.")
    return None

# Function to activate firmware update mode
def activate_firmware_update_mode(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Assuming the firmware update mode is controlled by a specific tag
            # Replace 'FirmwareUpdateMode' with the actual tag name
            plc.write('FirmwareUpdateMode', True)
            print(f"Firmware update mode activated on PLC at IP: {plc_ip}")
    except Exception as e:
        print(f"Failed to activate firmware update mode: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Activate firmware update mode
        activate_firmware_update_mode(plc_ip)

if __name__ == "__main__":
    main()