import socket
import OpenOPC

def discover_plc_ip():
    # This function simulates the discovery of the PLC's IP address.
    # In a real scenario, you might use ARP scanning or other network discovery methods.
    # For simplicity, we'll assume the IP address is known or manually input.
    plc_ip = input("Enter the PLC's IP address: ")
    return plc_ip

def connect_to_opc_server(ip_address):
    try:
        opc = OpenOPC.client()
        opc.connect('Matrikon.OPC.Simulation')  # Replace with your OPC server name
        print(f"Connected to OPC server for PLC at {ip_address}")
        return opc
    except Exception as e:
        print(f"Failed to connect to OPC server: {e}")
        return None

def enumerate_and_collect_data(opc):
    try:
        # Enumerate OPC tags (items) available on the PLC
        tags = opc.list()
        print("Available OPC Tags:")
        for tag in tags:
            print(tag)

        # Collect data from selected tags
        selected_tags = ['Channel1.Device1.Tag1', 'Channel1.Device1.Tag2']  # Replace with actual tags
        values = opc.read(selected_tags)
        print("Collected Data:")
        for tag, value in zip(selected_tags, values):
            print(f"{tag}: {value}")

    except Exception as e:
        print(f"Error during enumeration and data collection: {e}")

def main():
    # Step 1: Discover PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Failed to discover PLC IP address.")
        return

    # Step 2: Connect to OPC server
    opc = connect_to_opc_server(plc_ip)
    if not opc:
        return

    # Step 3: Enumerate and collect data
    enumerate_and_collect_data(opc)

    # Step 4: Close OPC connection
    opc.close()
    print("OPC connection closed.")

if __name__ == "__main__":
    main()