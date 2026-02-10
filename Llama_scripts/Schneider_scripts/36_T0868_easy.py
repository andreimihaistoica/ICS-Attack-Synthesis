import socket
import random
from pyopcuapy import client
import snap7

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # and the subnet mask is 255.255.255.0
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, 102))
            client.close()
            return ip
        except ConnectionRefusedError:
            pass
    return None

# Function to detect the operating mode of the PLC
def detect_operating_mode(plc_ip):
    # Create a S7 client object
    s7_client = snap7.S7Client()

    # Connect to the S7 server
    s7_client.ConnectTo(plc_ip, 0, 1)

    # Get the current operating mode
    operating_mode = s7_client.GetOperatingMode()

    # Print the current operating mode
    if operating_mode == snap7.s7const.S7CpuStatusRun:
        print("PLC is in Run mode")
    elif operating_mode == snap7.s7const.S7CpuStatusStop:
        print("PLC is in Stop mode")
    elif operating_mode == snap7.s7const.S7CpuStatusProg:
        print("PLC is in Program mode")
    elif operating_mode == snap7.s7const.S7CpuStatusRemote:
        print("PLC is in Remote mode")
    elif operating_mode == snap7.s7const.S7CpuStatusTest:
        print("PLC is in Test/Monitor mode")
    else:
        print("Unknown operating mode")

    # Disconnect from the S7 server
    s7_client.Disconnect()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        detect_operating_mode(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()