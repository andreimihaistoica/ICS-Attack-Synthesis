import netifaces as ni
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to find the PLC's IP address
def find_plc_ip():
    # List of common PLC IP addresses to check
    common_ips = ['192.168.0.1', '192.168.1.1', '192.168.100.1', '192.168.1.100']
    
    for ip in common_ips:
        try:
            client = ModbusTcpClient(ip)
            client.connect()
            if client.is_socket_open():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
    print("PLC not found. Please check the network configuration.")
    return None

# Function to collect point and tag values
def collect_point_tag_values(plc_ip):
    client = ModbusTcpClient(plc_ip)
    client.connect()
    
    if not client.is_socket_open():
        print("Failed to connect to the PLC.")
        return
    
    # Example tags and their corresponding Modbus addresses
    tags = {
        'Input1': 0x0000,  # Example input address
        'Output1': 0x0001, # Example output address
        'Memory1': 0x0002, # Example memory address
        'Variable1': 0x0003 # Example variable address
    }
    
    collected_values = {}
    
    for tag, address in tags.items():
        try:
            result = client.read_holding_registers(address, 1, unit=1)
            if result.isError():
                print(f"Error reading {tag} at address {address}")
            else:
                collected_values[tag] = result.registers[0]
                print(f"Collected {tag}: {collected_values[tag]}")
        except Exception as e:
            print(f"Error reading {tag} at address {address}: {e}")
    
    client.close()
    return collected_values

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        collected_values = collect_point_tag_values(plc_ip)
        print("Collected Point and Tag Values:")
        for tag, value in collected_values.items():
            print(f"{tag}: {value}")

if __name__ == "__main__":
    main()