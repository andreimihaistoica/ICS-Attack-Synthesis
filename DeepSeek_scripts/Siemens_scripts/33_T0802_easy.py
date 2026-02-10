import socket
from opcua import Client

def discover_plc_ip():
    """
    Discover the PLC's IP address by scanning the network.
    This is a placeholder function; you can replace it with a more robust implementation.
    """
    # Example: Scan a subnet for the PLC (replace with your network range)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            # Attempt to connect to the PLC's OPC UA port (default: 4840)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 4840))
            if result == 0:
                print(f"Discovered PLC at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            print(f"Error scanning IP {ip}: {e}")
    raise Exception("PLC IP address not found on the network.")

def collect_data_from_plc(plc_ip):
    """
    Connect to the PLC using OPC UA and collect data.
    """
    try:
        # Connect to the OPC UA server
        url = f"opc.tcp://{plc_ip}:4840"
        client = Client(url)
        client.connect()

        print(f"Connected to OPC UA server at {url}")

        # Browse the OPC UA node tree to enumerate devices and collect data
        root = client.get_root_node()
        print("Root node:", root)

        # Example: Browse all child nodes recursively
        print("Browsing nodes...")
        nodes = root.get_children()
        for node in nodes:
            print(f"Node: {node}, ID: {node.nodeid}, BrowseName: {node.get_browse_name()}")

        # Example: Read a specific node's value (replace with the actual node ID)
        node_id = "ns=2;s=ExampleNode"  # Replace with the actual node ID
        value = client.get_node(node_id).get_value()
        print(f"Value of node {node_id}: {value}")

    except Exception as e:
        print(f"Error collecting data from PLC: {e}")
    finally:
        client.disconnect()

def main():
    # Step 1: Discover the PLC's IP address (if not provided)
    plc_ip = discover_plc_ip()

    # Step 2: Connect to the PLC and collect data
    if plc_ip:
        collect_data_from_plc(plc_ip)

if __name__ == "__main__":
    main()