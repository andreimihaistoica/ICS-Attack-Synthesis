import pycomm3
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # This is a simple method to find the PLC's IP address
    # In a real-world scenario, you might use a more sophisticated method
    # such as scanning the network or using a known IP range
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = f"{ip_range}{i}"
        try:
            # Attempt to connect to the PLC
            with pycomm3.LogixDriver(ip) as plc:
                if plc.info:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    return None

# Function to modify alarm settings
def modify_alarm_settings(plc_ip):
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Example: Disable a specific alarm by setting a boolean tag to FALSE
            plc.write(('Alarm_Enabled', False))
            print("Alarm settings modified successfully.")
    except Exception as e:
        print(f"Failed to modify alarm settings: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Modify the alarm settings
        modify_alarm_settings(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()