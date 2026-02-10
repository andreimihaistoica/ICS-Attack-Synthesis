import socket
from opcua import Client

def discover_plc_ip():
    # Broadcast a message to discover the PLC's IP address
    # This is a simplified example; in a real-world scenario, you might use a more sophisticated method
    broadcast_ip = "255.255.255.255"
    port = 44818  # Common port for Allen-Bradley PLCs
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)
    
    try:
        # Send a broadcast message
        sock.sendto(b"DISCOVER_PLC", (broadcast_ip, port))
        
        # Receive a response from the PLC
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Discovered PLC IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC discovery timed out. Please check network settings.")
        return None
    finally:
        sock.close()

def collect_plc_data(plc_ip):
    # Connect to the PLC using OPC UA
    opcua_url = f"opc.tcp://{plc_ip}:4840"
    client = Client(opcua_url)
    
    try:
        client.connect()
        print(f"Connected to PLC at {opcua_url}")
        
        # Browse the OPC UA server for nodes
        root = client.get_root_node()
        print("Browsing OPC UA server nodes...")
        for node in root.get_children():
            print(f"Node: {node}")
        
        # Collect data from specific nodes (example)
        # Replace 'ns=2;i=1' with the actual node ID you want to read
        node_id = "ns=2;i=1"
        node = client.get_node(node_id)
        value = node.get_value()
        print(f"Value from node {node_id}: {value}")
        
    except Exception as e:
        print(f"Error collecting data from PLC: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        collect_plc_data(plc_ip)