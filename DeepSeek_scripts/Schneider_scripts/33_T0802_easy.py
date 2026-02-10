import socket
from opcua import Client

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Replace this with your network scanning logic
    # Example: Scanning a specific subnet for the PLC
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            # Attempt to connect to the PLC on a known port (e.g., 4840 for OPC UA)
            socket.create_connection((ip, 4840), timeout=1)
            print(f"Found PLC at IP: {ip}")
            return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    raise Exception("PLC not found on the network.")

# Function to collect data from the PLC using OPC UA
def collect_data_from_plc(plc_ip):
    # OPC UA server endpoint
    url = f"opc.tcp://{plc_ip}:4840"

    # Connect to the OPC UA server
    client = Client(url)
    try:
        client.connect()

        # Browse the OPC UA server for available nodes
        root = client.get_root_node()
        print("Browsing nodes in the OPC UA server:")
        for node in root.get_children():
            print(f"Node: {node.get_browse_name().Name}")

        # Example: Collect data from a specific node
        # Replace "ns=2;i=1" with the actual node ID you want to read
        node_id = "ns=2;i=1"
        node = client.get_node(node_id)
        value = node.get_value()
        print(f"Value of node {node_id}: {value}")

    finally:
        client.disconnect()

# Main script
if __name__ == "__main__":
    try:
        # Step 1: Discover the PLC's IP address
        plc_ip = discover_plc_ip()

        # Step 2: Collect data from the PLC using OPC UA
        collect_data_from_plc(plc_ip)
    except Exception as e:
        print(f"Error: {e}")