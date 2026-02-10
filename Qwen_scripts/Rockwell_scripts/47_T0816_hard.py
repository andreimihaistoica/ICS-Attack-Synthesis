import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (example: 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with LogixDriver(ip) as plc:
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to restart the PLC
def restart_plc(ip):
    try:
        with LogixDriver(ip) as plc:
            if plc.open():
                # Send the command to restart the PLC
                plc.write_tag('ControlWord', 0x01)  # Example control word for restart
                print(f"Restart command sent to PLC at IP: {ip}")
            else:
                print(f"Failed to connect to PLC at IP: {ip}")
    except Exception as e:
        print(f"Error restarting PLC: {e}")

# Function to shut down the PLC
def shutdown_plc(ip):
    try:
        with LogixDriver(ip) as plc:
            if plc.open():
                # Send the command to shut down the PLC
                plc.write_tag('ControlWord', 0x02)  # Example control word for shutdown
                print(f"Shutdown command sent to PLC at IP: {ip}")
            else:
                print(f"Failed to connect to PLC at IP: {ip}")
    except Exception as e:
        print(f"Error shutting down PLC: {e}")

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
        print("PLC not found. Exiting.")

if __name__ == "__main__":
    main()