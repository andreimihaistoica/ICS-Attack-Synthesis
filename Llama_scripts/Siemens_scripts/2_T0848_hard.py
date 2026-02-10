import socket
import struct
import snap7

# Define the PLC's IP address and port
plc_ip = None
plc_port = 102

# Define the command message to send to the PLC
command_message = b"\x01\x00\x00\x00\x00\x00\x00\x00"

# Function to scan the network for the PLC's IP address
def find_plc_ip():
    global plc_ip
    # Send a broadcast message to the network to find the PLC
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b"Hello, PLC!", ("255.255.255.255", plc_port))
    # Listen for a response from the PLC
    sock.settimeout(1)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP address {plc_ip}")
    except socket.timeout:
        print("No PLC found on the network")
    sock.close()

# Function to send the command message to the PLC
def send_command_message():
    global plc_ip
    if plc_ip is not None:
        # Create a client object
        client = snap7.S7Client()
        # Connect to the PLC
        client.ConnectTo(plc_ip, 0, 1)
        # Send the command message
        client.WriteArea(snap7.S7AreaMK, 0, 0, b"\x01")  # Set Activate_Fan_A to True
        client.WriteArea(snap7.S7AreaMK, 0, 1, b"\x01")  # Set Activate_Fan_B to True
        client.WriteArea(snap7.S7AreaDB, 7, 0, b"\x01\x3C")  # Set Motor_Temp to 300
        print("Command message sent to PLC")
        # Disconnect from the PLC
        client.Disconnect()
    else:
        print("PLC IP address not found")

# Function to read the PLC's tags
def read_plc_tags():
    global plc_ip
    if plc_ip is not None:
        # Create a client object
        client = snap7.S7Client()
        # Connect to the PLC
        client.ConnectTo(plc_ip, 0, 1)
        # Read the PLC's tags
        fan_a = client.ReadArea(snap7.S7AreaQ, 0, 0, 1)
        fan_b = client.ReadArea(snap7.S7AreaQ, 0, 1, 1)
        motor_temp = client.ReadArea(snap7.S7AreaMW, 7, 0, 2)
        print(f"Fan A: {fan_a}")
        print(f"Fan B: {fan_b}")
        print(f"Motor Temp: {motor_temp}")
        # Disconnect from the PLC
        client.Disconnect()
    else:
        print("PLC IP address not found")

# Main function
def main():
    find_plc_ip()
    send_command_message()
    read_plc_tags()

if __name__ == "__main__":
    main()