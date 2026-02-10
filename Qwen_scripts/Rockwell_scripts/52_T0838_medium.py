import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the subnet and range to scan
    subnet = '192.168.1.'
    start_ip = 1
    end_ip = 254

    for i in range(start_ip, end_ip + 1):
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

    print("PLC not found in the specified range.")
    return None

# Function to modify alarm settings
def modify_alarm_settings(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Example: Disable a specific alarm (tag name: 'Alarm1')
            plc.write(('Alarm1', 0))  # Set the alarm to 0 (disabled)
            print("Alarm settings modified successfully.")
    except Exception as e:
        print(f"Error modifying alarm settings: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_alarm_settings(plc_ip)

if __name__ == "__main__":
    main()