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
            # Attempt to connect to the PLC
            with PLC(ip) as plc:
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Failed to connect to {ip}: {e}")
    return None

# Function to restart the PLC
def restart_plc(ip):
    try:
        with PLC(ip) as plc:
            if plc.open():
                # Send the command to restart the PLC
                plc.write("M0.0", True)  # Example: Write to a specific memory bit to trigger a restart
                print(f"Restart command sent to PLC at IP: {ip}")
            else:
                print(f"Failed to open connection to PLC at IP: {ip}")
    except Exception as e:
        print(f"Failed to restart PLC at IP: {ip}. Error: {e}")

# Function to shut down the PLC
def shutdown_plc(ip):
    try:
        with PLC(ip) as plc:
            if plc.open():
                # Send the command to shut down the PLC
                plc.write("M0.1", True)  # Example: Write to a specific memory bit to trigger a shutdown
                print(f"Shutdown command sent to PLC at IP: {ip}")
            else:
                print(f"Failed to open connection to PLC at IP: {ip}")
    except Exception as e:
        print(f"Failed to shut down PLC at IP: {ip}. Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Choose to restart or shut down the PLC
        action = input("Enter 'restart' to restart the PLC or 'shutdown' to shut down the PLC: ").strip().lower()
        if action == 'restart':
            restart_plc(plc_ip)
        elif action == 'shutdown':
            shutdown_plc(plc_ip)
        else:
            print("Invalid action. Please enter 'restart' or 'shutdown'.")
    else:
        print("PLC not found in the specified subnet range.")

if __name__ == "__main__":
    main()