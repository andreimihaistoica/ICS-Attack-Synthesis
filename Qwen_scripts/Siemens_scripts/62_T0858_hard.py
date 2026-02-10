import pycomm3
from pycomm3 import LogixDriver, S7Client
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with S7Client(ip) as client:
                if client.is_connected:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to change the operating mode of the PLC
def change_operating_mode(ip, mode):
    with S7Client(ip) as client:
        if client.is_connected:
            if mode == "Program":
                client.plc_stop()
                client.plc_hot_start()
                print(f"PLC at {ip} is now in Program mode.")
            elif mode == "Run":
                client.plc_cold_start()
                print(f"PLC at {ip} is now in Run mode.")
            else:
                print("Invalid mode. Use 'Program' or 'Run'.")
        else:
            print(f"Failed to connect to PLC at {ip}.")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Change the operating mode to Program
        change_operating_mode(plc_ip, "Program")
        time.sleep(2)  # Wait for the mode change to take effect
        # Optionally, change back to Run mode
        change_operating_mode(plc_ip, "Run")

if __name__ == "__main__":
    main()