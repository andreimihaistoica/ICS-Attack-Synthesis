import nmap
from pymodbus.client import ModbusTcpClient
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 502')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            print(f"PLC found at IP: {host}")
            return host
    return None

# Function to connect to the PLC and modify the program
def modify_plc_program(plc_ip):
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    try:
        # Example: Modify a specific register (for demonstration purposes)
        # Replace the register address and value as needed
        register_address = 0x0001
        new_value = 0x1234

        # Write the new value to the register
        result = client.write_register(register_address, new_value)
        if result.isError():
            print("Failed to modify the PLC program.")
        else:
            print("PLC program modified successfully.")
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_plc_program(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()