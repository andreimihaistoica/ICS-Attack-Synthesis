import nmap
from opcua import Client, ua

# Function to find the PLC's IP address
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 4840')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if nm[host].has_tcp(4840) and nm[host]['tcp'][4840]['state'] == 'open':
            return host
    return None

# Function to connect to the PLC and collect information
def collect_plc_info(plc_ip):
    client = Client(f"opc.tcp://{plc_ip}:4840")
    try:
        client.connect()
        print(f"Connected to PLC at {plc_ip}")

        # Enumerate and collect information
        root = client.get_root_node()
        objects = client.get_objects_node()
        variables = objects.get_children()

        for var in variables:
            var_name = var.get_browse_name().Name
            var_value = var.get_value()
            print(f"Variable: {var_name}, Value: {var_value}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        collect_plc_info(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()