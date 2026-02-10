import nmap
from opcua import Client

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-p 102')  # Port 102 is commonly used by S7-1200 PLC
    for host in nm.all_hosts():
        if nm[host].has_tcp(102) and nm[host]['tcp'][102]['state'] == 'open':
            return host
    return None

# Function to connect to the PLC and enumerate information
def collect_plc_info(plc_ip):
    client = Client(f"opc.tcp://{plc_ip}:4840")
    try:
        client.connect()
        print(f"Connected to PLC at {plc_ip}")

        # Enumerate and gather information
        root = client.get_root_node()
        objects = client.get_objects_node()
        print("Root Node:", root)
        print("Objects Node:", objects)

        # Example: List all nodes under the Objects node
        for node in objects.get_children():
            print(f"Node: {node}, Node ID: {node.nodeid}, Node Name: {node.get_browse_name()}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()

# Main function
def main():
    subnet = "192.168.1.0/24"  # Change this to your network subnet
    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        collect_plc_info(plc_ip)
    else:
        print("PLC not found in the specified subnet.")

if __name__ == "__main__":
    main()