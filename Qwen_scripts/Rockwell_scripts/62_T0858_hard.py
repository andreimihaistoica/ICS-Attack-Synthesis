import pycomm3
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (adjust as needed)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with pycomm3.CipDriver(ip) as driver:
                if driver.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to change the operating mode of the PLC
def change_operating_mode(ip, mode):
    with pycomm3.CipDriver(ip) as driver:
        if driver.open():
            # Change the operating mode
            result = driver.set_plc_mode(mode)
            if result:
                print(f"Operating mode changed to {mode}")
            else:
                print(f"Failed to change operating mode to {mode}")
        else:
            print("Failed to connect to the PLC")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Change the operating mode to "Program"
        change_operating_mode(plc_ip, 'PROGRAM')
        # Optionally, you can add a delay to ensure the mode change is effective
        time.sleep(2)
        # Change the operating mode back to "Run" after performing necessary operations
        change_operating_mode(plc_ip, 'RUN')

if __name__ == "__main__":
    main()