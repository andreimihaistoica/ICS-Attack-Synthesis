import snap7
from snap7.util import *
import socket

# Function to find the PLC's IP address
def find_plc_ip():
    # Replace with the actual subnet of your network
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            # Try to connect to the PLC on port 102 (default for Siemens S7)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 102))
                print(f"PLC found at IP: {ip}")
                return ip
        except:
            continue
    print("PLC not found on the network.")
    return None

# Function to change the PLC's operating mode
def change_plc_mode(ip, mode):
    try:
        # Create a PLC client
        plc = snap7.client.Client()
        plc.connect(ip, 0, 1)  # Connect to the PLC (Rack 0, Slot 1)

        # Change the operating mode
        if mode == "Program":
            plc.plc_stop()  # Stop the PLC to change to Program mode
            print("PLC changed to Program Mode.")
        elif mode == "Run":
            plc.plc_run()  # Change to Run mode
            print("PLC changed to Run Mode.")
        elif mode == "Remote":
            plc.plc_cold_start()  # Change to Remote mode (cold start)
            print("PLC changed to Remote Mode.")
        elif mode == "Stop":
            plc.plc_stop()  # Change to Stop mode
            print("PLC changed to Stop Mode.")
        elif mode == "Reset":
            plc.plc_cold_start()  # Change to Reset mode (cold start)
            print("PLC reset to default state.")
        elif mode == "Test":
            plc.plc_hot_start()  # Change to Test/Monitor mode (hot start)
            print("PLC changed to Test/Monitor Mode.")
        else:
            print("Invalid mode specified.")

        # Disconnect from the PLC
        plc.disconnect()
    except Exception as e:
        print(f"Error changing PLC mode: {e}")

# Main script
if __name__ == "__main__":
    # Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Change the PLC's operating mode to Program mode
        change_plc_mode(plc_ip, "Program")