import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the engineering workstation
    # This is a simple example using a broadcast to find the PLC
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = f"{ip_range}{i}"
        try:
            # Attempt to connect to the IP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((ip, 44818))  # 44818 is the default port for EtherNet/IP
                return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    return None

# Function to perform an online edit to the PLC
def perform_online_edit(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Check if the PLC is in the correct mode (RUN)
            if plc.get_plc_state() != 'RUN':
                print("PLC is not in RUN mode. Changing to RUN mode.")
                plc.set_plc_state('RUN')

            # Example of an online edit: Modify a tag value
            tag_name = 'ExampleTag'
            new_value = 12345
            plc.write((tag_name, new_value))

            print(f"Online edit successful. Tag '{tag_name}' set to {new_value}.")
    except Exception as e:
        print(f"Error performing online edit: {e}")

# Main function
def main():
    print("Discovering PLC IP address...")
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        perform_online_edit(plc_ip)
    else:
        print("PLC not found. Please check the network configuration.")

if __name__ == "__main__":
    main()