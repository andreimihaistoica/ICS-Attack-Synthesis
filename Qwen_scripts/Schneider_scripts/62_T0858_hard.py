import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    subnet = "192.168.9.0/24"
    ip_list = [f"192.168.9.{i}" for i in range(1, 255)]
    
    for ip in ip_list:
        try:
            # Attempt to connect to the Modbus TCP port (502)
            with socket.create_connection((ip, 502), timeout=1) as sock:
                print(f"PLC found at IP: {ip}")
                return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("PLC not found on the network.")
    return None

# Function to change the operating mode to "Program" mode
def change_operating_mode(ip, mode):
    client = ModbusTcpClient(ip)
    
    try:
        client.connect()
        
        # Define the holding register address for the operating mode
        # This address may vary depending on the PLC model and configuration
        # For the TM221CE16R, the operating mode might be set via a specific register
        # Here, we assume the register address is 0x0000 (you may need to check the documentation)
        register_address = 0x0000
        
        # Define the mode values
        # 0: Run
        # 1: Program
        # 2: Stop
        # 3: Reset
        # 4: Test/Monitor
        mode_values = {
            "Run": 0,
            "Program": 1,
            "Stop": 2,
            "Reset": 3,
            "Test/Monitor": 4
        }
        
        # Write the mode value to the register
        result = client.write_register(register_address, mode_values[mode])
        
        if result.isError():
            print(f"Failed to change operating mode to {mode}.")
        else:
            print(f"Operating mode changed to {mode}.")
    
    except ConnectionException:
        print("Failed to connect to the PLC.")
    
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Change the operating mode to "Program" mode
        change_operating_mode(plc_ip, "Program")

if __name__ == "__main__":
    main()