import socket
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to find the PLC's IP address
def find_plc_ip():
    # This is a placeholder function. In a real scenario, you would use network scanning tools
    # to find the PLC's IP address. For simplicity, we'll assume the PLC is at a known IP.
    return '192.168.1.100'

# Function to change the PLC's password
def change_plc_password(plc_ip, new_password):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print(f"Failed to connect to PLC at {plc_ip}")
            return

        # Example: Change the password (this is a placeholder for the actual Modbus function)
        # Note: The actual register and function code to change the password will depend on the PLC's documentation
        # For this example, we'll assume the password is stored in register 1000
        password_register = 1000
        client.write_register(password_register, new_password)

        # Verify the password change
        response = client.read_holding_registers(password_register, 1)
        if response.registers[0] == new_password:
            print(f"Password changed successfully to {new_password}")
        else:
            print("Failed to change password")

        # Close the connection
        client.close()
    except ConnectionException as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    print(f"PLC IP address: {plc_ip}")

    # New password to set
    new_password = 12345  # Example password, should be a more secure value in a real scenario

    # Change the PLC's password
    change_plc_password(plc_ip, new_password)

if __name__ == "__main__":
    main()