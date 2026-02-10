import socket
import random
from pyopcuapy import client
import snap7

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # and the subnet mask is 255.255.255.0
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, 102))
            client.close()
            return ip
        except ConnectionRefusedError:
            pass
    return None

# Function to collect information from the PLC using OPC
def collect_information(plc_ip):
    # Create an OPC client object
    opc_client = client.OPCClient(plc_ip, 48010)

    # Connect to the OPC server
    opc_client.connect()

    # Get the list of available nodes
    nodes = opc_client.get_nodes()

    # Print the list of available nodes
    print(nodes)

    # Get the value of a specific node
    node_value = opc_client.read_node("ns=2;i=1")

    # Print the value of the node
    print(node_value)

    # Get the list of available variables
    variables = opc_client.get_variables()

    # Print the list of available variables
    print(variables)

    # Get the value of a specific variable
    variable_value = opc_client.read_variable("ns=2;i=1")

    # Print the value of the variable
    print(variable_value)

    # Disconnect from the OPC server
    opc_client.disconnect()

    # Create a S7 client object
    s7_client = snap7.S7Client()

    # Connect to the S7 server
    s7_client.ConnectTo(plc_ip, 0, 1)

    # Get the list of available blocks
    blocks = s7_client.GetBlockInfo()

    # Print the list of available blocks
    print(blocks)

    # Get the value of a specific block
    block_value = s7_client.ReadArea(snap7.s7const.S7AreaDB, 1, 0)

    # Print the value of the block
    print(block_value)

    # Disconnect from the S7 server
    s7_client.Disconnect()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        collect_information(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()