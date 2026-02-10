import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # This is a simple example using a broadcast to find the PLC
    # In a real-world scenario, you might use a more sophisticated method
    broadcast_ip = '255.255.255.255'
    port = 502  # Modbus TCP port

    # Create a socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to the PLC
    message = b'PLC_DISCOVERY'
    sock.sendto(message, (broadcast_ip, port))

    # Receive the response
    sock.settimeout(5)  # Set a timeout for the response
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None

# Function to modify alarm settings on the PLC
def modify_alarm_settings(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        client.connect()

        # Example: Disable a specific alarm (assuming the alarm is controlled by a specific register)
        # Modify the register address and value as per your PLC's configuration
        register_address = 0x0001  # Example register address
        new_value = 0  # Example value to disable the alarm

        # Write the new value to the register
        result = client.write_register(register_address, new_value)
        if result.isError():
            print("Failed to modify alarm settings")
        else:
            print("Alarm settings modified successfully")

        # Close the connection
        client.close()
    except ConnectionException as e:
        print(f"Connection error: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_alarm_settings(plc_ip)

if __name__ == "__main__":
    main()