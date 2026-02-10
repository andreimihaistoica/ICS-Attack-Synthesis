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

# Function to change credentials on the PLC
def change_credentials(client, new_username, new_password):
    try:
        # Get the current credentials
        current_credentials = client.read_holding_registers(0x1000, 2)
        current_username = current_credentials.registers[0]
        current_password = current_credentials.registers[1]
        
        # Change the credentials
        client.write_register(0x1000, new_username)
        client.write_register(0x1001, new_password)
        print("Credentials changed on PLC")
    except Exception as e:
        print(f"Failed to change credentials on PLC: {e}")

# Function to read a register on the PLC
def read_register(client, register_address):
    try:
        current_value = client.read_holding_registers(register_address, 1)
        current_value = current_value.registers[0]
        print(f"Current register value at address {register_address}: {current_value}")
    except Exception as e:
        print(f"Failed to read register at address {register_address}: {e}")

# Main function
def main():
    plc_ip_address = find_plc_ip()
    if plc_ip_address:
        client = ModbusTcpClient(plc_ip_address)
        connection = client.connect()
        print(f"Connected to PLC: {connection}")
        new_username = 0x1234  # Replace with the new username
        new_password = 0x5678  # Replace with the new password
        change_credentials(client, new_username, new_password)
        register_address = 0x1000
        read_register(client, register_address)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()