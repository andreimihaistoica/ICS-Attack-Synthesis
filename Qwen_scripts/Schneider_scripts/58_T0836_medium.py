import nmap
from pymodbus.client import ModbusTcpClient
import time

# Function to scan the network and find the PLC's IP address
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 502')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            print(f"PLC found at IP: {host}")
            return host
    print("PLC not found on the network.")
    return None

# Function to modify a parameter on the PLC
def modify_parameter(plc_ip, register_address, new_value):
    client = ModbusTcpClient(plc_ip)
    if client.connect():
        try:
            # Write the new value to the specified register
            result = client.write_register(register_address, new_value)
            if result.isError():
                print(f"Failed to modify parameter at register {register_address}")
            else:
                print(f"Parameter at register {register_address} modified to {new_value}")
        finally:
            client.close()
    else:
        print(f"Failed to connect to PLC at IP: {plc_ip}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        # Example: Modify the parameter at register 0x0001 to 1000
        register_address = 0x0001
        new_value = 1000
        modify_parameter(plc_ip, register_address, new_value)

if __name__ == "__main__":
    main()