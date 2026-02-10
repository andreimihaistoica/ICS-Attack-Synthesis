import socket
import struct

# Function to find the PLC's IP address (simplified for demonstration)
def find_plc_ip():
    # Replace this with actual discovery logic (e.g., ARP scan, network broadcast)
    # For demonstration, we assume the PLC's IP is known or provided by the user.
    plc_ip = input("Enter the PLC's IP address: ")
    return plc_ip

# Function to modify alarm settings on the PLC
def modify_alarm_settings(plc_ip, alarm_id, new_setting):
    try:
        # Establish a connection to the PLC (using a simple socket for demonstration)
        plc_port = 502  # Default Modbus TCP port
        plc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plc_socket.connect((plc_ip, plc_port))
        print(f"Connected to PLC at {plc_ip}:{plc_port}")

        # Craft a Modbus TCP packet to modify alarm settings
        # This is a simplified example and may not work for all PLCs
        transaction_id = 0x0001  # Arbitrary transaction ID
        protocol_id = 0x0000  # Modbus protocol ID
        unit_id = 0x01  # PLC unit ID
        function_code = 0x06  # Write single register
        register_address = alarm_id  # Alarm register address
        register_value = new_setting  # New alarm setting value

        # Build the Modbus packet
        packet = struct.pack(">HHHBBHH", transaction_id, protocol_id, 6, unit_id, function_code, register_address, register_value)
        plc_socket.send(packet)

        # Receive the response (if any)
        response = plc_socket.recv(1024)
        print(f"Response from PLC: {response.hex()}")

        # Close the connection
        plc_socket.close()
        print(f"Alarm settings modified successfully for Alarm ID {alarm_id}.")

    except Exception as e:
        print(f"Error modifying alarm settings: {e}")

# Main function
def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Step 2: Define the alarm ID and new setting
    alarm_id = 1001  # Example alarm ID (replace with actual alarm ID)
    new_setting = 0  # Example new setting (0 = disable alarm)

    # Step 3: Modify the alarm settings on the PLC
    modify_alarm_settings(plc_ip, alarm_id, new_setting)

if __name__ == "__main__":
    main()