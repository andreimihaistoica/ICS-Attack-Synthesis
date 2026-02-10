import snap7
import snap7.client as c
from snap7.util import *
from snap7.types import *
import socket

def find_plc_ip():
    """
    Scans the network to find the PLC's IP address.
    This is a basic implementation and may need to be adjusted based on the network setup.
    """
    # Replace with the expected PLC IP range or use a more sophisticated method
    ip_range = "192.168.0."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 102))  # Port 102 is used by Siemens S7 protocol
                print(f"PLC found at IP: {ip}")
                return ip
        except:
            continue
    print("PLC IP address not found.")
    return None

def change_plc_mode(plc_ip, mode):
    """
    Changes the operating mode of the Siemens S7-1200 PLC.
    :param plc_ip: The IP address of the PLC.
    :param mode: The desired operating mode (e.g., 'Program', 'Run', etc.).
    """
    try:
        # Create a PLC client
        plc = c.Client()
        plc.connect(plc_ip, 0, 1)  # Connect to the PLC

        # Change the operating mode
        if mode == "Program":
            plc.plc_stop()  # Stop the PLC before changing to Program mode
            print("PLC changed to Program mode.")
        elif mode == "Run":
            plc.plc_run()  # Set the PLC to Run mode
            print("PLC changed to Run mode.")
        elif mode == "Stop":
            plc.plc_stop()  # Stop the PLC
            print("PLC changed to Stop mode.")
        else:
            print(f"Unsupported mode: {mode}")

        # Disconnect from the PLC
        plc.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address (if needed)
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Change the PLC's operating mode to "Program"
        change_plc_mode(plc_ip, "Program")
    else:
        print("Cannot proceed without PLC IP address.")