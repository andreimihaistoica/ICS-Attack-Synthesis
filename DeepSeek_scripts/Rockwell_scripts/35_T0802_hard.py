import OpenOPC
import socket
import time

def discover_plc_ip():
    """Discover the PLC's IP address on the network."""
    # This is a placeholder for the actual PLC IP discovery logic.
    # In a real-world scenario, you might use network scanning tools or ARP requests.
    # For simplicity, we assume the IP is known or manually input.
    plc_ip = input("Enter the PLC's IP address: ")
    return plc_ip

def collect_plc_data(plc_ip):
    """Collect data from the PLC using OPC."""
    try:
        # Initialize OPC client
        opc = OpenOPC.client()
        opc.connect('Matrikon.OPC.Simulation.1')  # Replace with the correct OPC server name

        # Enumerate tags available on the PLC
        tags = opc.list(plc_ip)
        print(f"Available tags on PLC {plc_ip}: {tags}")

        # Collect data from specific tags
        tag_values = {}
        for tag in tags:
            value, quality, timestamp = opc.read(tag)
            tag_values[tag] = {
                'value': value,
                'quality': quality,
                'timestamp': timestamp
            }

        # Print collected data
        print("Collected data from PLC:")
        for tag, data in tag_values.items():
            print(f"Tag: {tag}, Value: {data['value']}, Quality: {data['quality']}, Timestamp: {data['timestamp']}")

        # Close OPC connection
        opc.close()

    except Exception as e:
        print(f"Error collecting data from PLC: {e}")

def main():
    """Main function to discover PLC IP and collect data."""
    plc_ip = discover_plc_ip()
    print(f"Discovered PLC IP: {plc_ip}")

    # Collect data from PLC
    collect_plc_data(plc_ip)

if __name__ == "__main__":
    main()