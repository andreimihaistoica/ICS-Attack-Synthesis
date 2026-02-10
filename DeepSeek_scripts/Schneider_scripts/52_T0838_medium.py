import socket
from pymodbus.client import ModbusTcpClient

# Function to find the PLC's IP address on the network
def find_plc_ip():
    # Replace with the actual subnet of your network
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            # Attempt to connect to the PLC on port 502 (Modbus TCP)
            client = ModbusTcpClient(ip, port=502, timeout=1)
            if client.connect():
                print(f"Found PLC at IP: {ip}")
                client.close()
                return ip
        except Exception as e:
            print(f"Scanning {ip}: {e}")
    print("PLC not found on the network.")
    return None

# Function to modify alarm settings
def modify_alarm_settings(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip, port=502)
        if client.connect():
            print("Connected to the PLC.")
            
            # Modify alarm settings (example: disable alarms on register 40001)
            # Replace the register address and value with the appropriate ones for your PLC
            register_address = 40001
            new_value = 0  # 0 to disable the alarm
            client.write_register(register_address, new_value)
            print(f"Alarm settings modified on register {register_address}.")
            
            # Disconnect from the PLC
            client.close()
            print("Disconnected from the PLC.")
        else:
            print("Failed to connect to the PLC.")
    except Exception as e:
        print(f"Error modifying alarm settings: {e}")

# Main script execution
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Modify the alarm settings
        modify_alarm_settings(plc_ip)
    else:
        print("Cannot proceed without the PLC's IP address.")