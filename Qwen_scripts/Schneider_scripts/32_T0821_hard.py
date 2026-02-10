import pymodbus
from pymodbus.client import ModbusTcpClient
import netifaces as ni
import socket
import time

# Function to scan the network for the PLC
def find_plc_ip():
    # Get the IP address of the local machine
    local_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    network = '.'.join(local_ip.split('.')[:-1]) + '.0/24'
    
    # Scan the network for devices
    for i in range(1, 255):
        ip = f"{network[:-4]}{i}"
        try:
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except Exception as e:
            print(f"Error connecting to {ip}: {e}")
        finally:
            client.close()
    return None

# Function to connect to the PLC and modify the tasking
def modify_controller_tasking(plc_ip):
    client = ModbusTcpClient(plc_ip)
    
    if not client.connect():
        print("Failed to connect to the PLC.")
        return
    
    try:
        # Example: Modify the tasking to include a new program
        # This is a simplified example. In a real scenario, you would need to use the appropriate Modbus registers
        # and commands to modify the tasking.
        
        # Read the current tasking configuration (example register)
        tasking_register = 0x0001
        response = client.read_holding_registers(tasking_register, 1, unit=1)
        if response.isError():
            print("Error reading tasking configuration.")
            return
        
        current_tasking = response.registers[0]
        print(f"Current tasking configuration: {current_tasking}")
        
        # Modify the tasking configuration (example: add a new program)
        new_tasking = current_tasking | 0x0001  # Example: Set the least significant bit to 1
        response = client.write_register(tasking_register, new_tasking, unit=1)
        if response.isError():
            print("Error writing tasking configuration.")
            return
        
        print(f"Tasking configuration modified to: {new_tasking}")
    
    finally:
        client.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        modify_controller_tasking(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()