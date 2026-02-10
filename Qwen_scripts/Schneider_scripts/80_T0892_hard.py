import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
    return None

# Function to change the PLC's credentials
def change_plc_credentials(ip, new_username, new_password):
    client = ModbusTcpClient(ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    try:
        # Example: Change the username and password (this is a placeholder for the actual Modbus registers)
        # Note: The actual register addresses and values will depend on the PLC's configuration and firmware.
        # For this example, we assume the username and password are stored in registers 100 and 101 respectively.
        client.write_register(100, new_username)
        client.write_register(101, new_password)
        print(f"Credentials changed successfully. New username: {new_username}, New password: {new_password}")
    except Exception as e:
        print(f"Failed to change credentials: {e}")
    finally:
        client.close()

# Main function
def main():
    subnet = "192.168.9"
    new_username = "new_user"
    new_password = "new_password"

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        # Change the PLC's credentials
        change_plc_credentials(plc_ip, new_username, new_password)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()