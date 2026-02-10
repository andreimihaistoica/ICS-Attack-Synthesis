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

# Function to activate firmware update mode on the PLC
def activate_firmware_update_mode(client):
    try:
        # Send the command to activate firmware update mode
        client.write_register(0x1000, 0x01)
        print("Firmware update mode activated on PLC")
    except Exception as e:
        print(f"Failed to activate firmware update mode on PLC: {e}")

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
        activate_firmware_update_mode(client)
        register_address = 0x1000
        read_register(client, register_address)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()