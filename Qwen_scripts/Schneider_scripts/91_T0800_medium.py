import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to find the PLC's IP address
def find_plc_ip():
    # Define the subnet and range to scan
    subnet = "192.168.1."
    start_ip = 1
    end_ip = 254

    for i in range(start_ip, end_ip + 1):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            client = ModbusTcpClient(ip)
            client.connect()
            if client.is_socket_open():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
        finally:
            client.close()
    print("PLC not found in the specified range.")
    return None

# Function to activate firmware update mode
def activate_firmware_update_mode(plc_ip):
    try:
        client = ModbusTcpClient(plc_ip)
        client.connect()

        if client.is_socket_open():
            print("Connected to PLC.")

            # Define the register address and value to activate firmware update mode
            # Note: The actual register address and value may vary depending on the PLC model and firmware
            register_address = 0x0000  # Example register address
            value = 0x01  # Example value to activate firmware update mode

            # Write the value to the register
            result = client.write_register(register_address, value)
            if result.isError():
                print("Failed to activate firmware update mode.")
            else:
                print("Firmware update mode activated successfully.")
        else:
            print("Failed to connect to PLC.")
    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        activate_firmware_update_mode(plc_ip)

if __name__ == "__main__":
    main()