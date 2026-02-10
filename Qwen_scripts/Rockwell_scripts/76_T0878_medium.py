import pycomm3
from pycomm3 import LogixDriver
import socket
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # This is a simple example of finding the PLC's IP address.
    # In a real-world scenario, you might use a network scanner or a more sophisticated method.
    plc_ip = '192.168.1.10'  # Replace with the actual IP address of the PLC
    return plc_ip

# Function to suppress alarms
def suppress_alarms(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Example of suppressing an alarm by setting a specific tag to a fixed value
            # Replace 'AlarmTag' with the actual tag name in your PLC
            plc.write(('AlarmTag', 0))
            print("Alarm suppressed successfully.")
    except Exception as e:
        print(f"Error suppressing alarm: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    print(f"PLC IP address: {plc_ip}")

    # Suppress alarms
    suppress_alarms(plc_ip)

if __name__ == "__main__":
    main()