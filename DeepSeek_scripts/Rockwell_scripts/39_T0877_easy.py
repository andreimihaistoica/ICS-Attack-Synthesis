import snap7
import socket
from snap7.util import get_ip

def discover_plc_ip():
    """
    Discover the PLC's IP address on the network.
    This function is a placeholder and should be implemented based on your network setup.
    """
    # Example: Scan the local network for PLCs
    # This is a simple implementation and may need to be adapted for your network
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 102))  # Port 102 is commonly used for S7 communication
                print(f"PLC found at IP: {ip}")
                return ip
        except:
            continue
    raise Exception("PLC not found on the network")

def collect_io_image(plc_ip):
    """
    Collect the I/O Image from the PLC using its native API.
    """
    # Initialize the Snap7 client
    client = snap7.client.Client()
    
    try:
        # Connect to the PLC
        client.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (common for Siemens PLCs)
        
        # Read the input image table
        input_image = client.db_read(1, 0, 100)  # Read 100 bytes from DB1 (example)
        print("Input Image Table:", input_image)
        
        # Read the output image table
        output_image = client.db_read(2, 0, 100)  # Read 100 bytes from DB2 (example)
        print("Output Image Table:", output_image)
        
    except Exception as e:
        print(f"Error collecting I/O Image: {e}")
    finally:
        # Disconnect from the PLC
        client.disconnect()

def main():
    # Step 1: Discover the PLC's IP address (if not already known)
    plc_ip = discover_plc_ip()
    
    # Step 2: Collect the I/O Image from the PLC
    collect_io_image(plc_ip)

if __name__ == "__main__":
    main()