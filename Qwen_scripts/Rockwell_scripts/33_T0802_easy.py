import nmap
from opcua import Client

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-p 4840')  # OPC UA default port
    for host in nm.all_hosts():
        if nm[host].has_tcp(4840) and nm[host]['tcp'][4840]['state'] == 'open':
            return host
    return None

# Function to connect to the PLC and enumerate tags
def enumerate_opc_tags(plc_ip):
    client = Client(f"opc.tcp://{plc_ip}:4840")
    try:
        client.connect()
        root = client.get_root_node()
        objects = client.get_objects_node()
        print("Connected to PLC at:", plc_ip)
        print("Enumerating tags and devices...")

        # Enumerate objects and their children
        for obj in objects.get_children():
            print(f"Object: {obj.get_browse_name()}")
            for child in obj.get_children():
                print(f"  - {child.get_browse_name()}: {child.get_value()}")
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
    finally:
        client.disconnect()

# Main function
def main():
    subnet = "192.168.1.0/24"  # Change this to your network subnet
    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        enumerate_opc_tags(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()