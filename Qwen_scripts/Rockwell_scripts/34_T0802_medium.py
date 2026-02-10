import netifaces as ni
from opcua import Client, ua

def find_plc_ip():
    # List all network interfaces
    interfaces = ni.interfaces()
    
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            print(f"Checking IP: {ip}")
            
            # Try to connect to the PLC
            client = Client(f"opc.tcp://{ip}:4840")
            try:
                client.connect()
                print(f"PLC found at IP: {ip}")
                client.disconnect()
                return ip
            except Exception as e:
                print(f"Failed to connect to {ip}: {e}")
        except Exception as e:
            print(f"Error checking interface {interface}: {e}")
    
    print("PLC not found on any network interface.")
    return None

def collect_plc_info(plc_ip):
    if not plc_ip:
        print("No PLC IP found. Exiting.")
        return
    
    client = Client(f"opc.tcp://{plc_ip}:4840")
    
    try:
        client.connect()
        print(f"Connected to PLC at {plc_ip}")
        
        # Enumerate nodes
        root = client.get_root_node()
        objects = client.get_objects_node()
        
        print("Enumerating nodes...")
        for node in objects.get_children():
            print(f"Node: {node}")
            for child in node.get_children():
                print(f"  Child: {child} - Value: {child.get_value()}")
        
    except Exception as e:
        print(f"Error collecting PLC information: {e}")
    finally:
        client.disconnect()
        print("Disconnected from PLC")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    collect_plc_info(plc_ip)