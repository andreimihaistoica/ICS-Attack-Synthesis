# MITRE ATT&CK T1005: Data from Local System
# COLLECTION: Automated Collection - Industrial Environment (PLC Data)

# This script is designed to run on a Windows machine with network connectivity
# to the PLC.  It assumes the existence of an OPC UA server on the PLC.
#
# Pre-requisites:
# 1.  Install the `opcua` library: `pip install opcua`
# 2.  Ensure the PLC's OPC UA server is configured and running.  You'll need the
#     endpoint URL of the OPC UA server. This script uses UDP broadcast to attempt PLC IP discovery.
#     If the PLC is not configured for UDP broadcast IP discovery or firewall rules block it,
#     hardcode the PLC IP address.
#
# Disclaimer: This script is for educational and demonstration purposes ONLY.
# Use it responsibly and ethically.  Unauthorized access to or disruption
# of industrial control systems can have serious consequences.  Always obtain
# proper authorization before running any scripts on production systems.

import socket
import time
from opcua import Client
from opcua import ua

# Configuration
BROADCAST_ADDRESS = '<broadcast>'  # Use '<broadcast>' for all networks.  Adjust if needed.
BROADCAST_PORT = 49152  # Example port. May need to be adjusted based on PLC setup.
BROADCAST_MESSAGE = b"PLC_IP_DISCOVERY"  # Message to send for PLC IP discovery
TIMEOUT_SECONDS = 5       # Time to wait for a PLC response
OPC_UA_PORT = 4840       # Standard OPC UA port.  Adjust if needed.

# Function to attempt to discover the PLC's IP address via UDP broadcast.
def discover_plc_ip():
    """Attempts to discover the PLC's IP address using UDP broadcast."""
    print("Attempting to discover PLC IP address via UDP broadcast...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(TIMEOUT_SECONDS)

    try:
        sock.sendto(BROADCAST_MESSAGE, (BROADCAST_ADDRESS, BROADCAST_PORT))
        print(f"Broadcast message sent to {BROADCAST_ADDRESS}:{BROADCAST_PORT}")

        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        plc_ip = addr[0]
        print(f"Received response from PLC: {plc_ip}")
        return plc_ip

    except socket.timeout:
        print("Timeout: No response received from PLC after {} seconds.".format(TIMEOUT_SECONDS))
        return None
    except Exception as e:
        print(f"Error during UDP broadcast: {e}")
        return None
    finally:
        sock.close()


def collect_plc_data(plc_ip_address):
    """Collects data from the PLC's OPC UA server."""

    opc_ua_endpoint = f"opc.tcp://{plc_ip_address}:{OPC_UA_PORT}"  # Construct OPC UA endpoint URL
    print(f"Connecting to OPC UA server at: {opc_ua_endpoint}")


    try:
        client = Client(opc_ua_endpoint)
        client.connect()

        print("Successfully connected to OPC UA server.")

        # Get the root node
        root = client.get_root_node()
        print("Root node: ", root)

        # Get the objects node
        objects = client.get_objects_node()
        print("Objects node: ", objects)

        # Browse the address space.  Adjust these paths based on the PLC's OPC UA server structure.
        #  This is a critical step! You MUST know the structure of the PLC's OPC UA server.
        #  Example paths:
        #  - 'ns=4;i=2',  # Example: Data from namespace 4, identifier 2
        #  - ['0:Objects', '2:MyDevice', '3:Temperature'] # hierarchical browsing
        #  - 'ns=2;s=Channel1.Device1.Tag1' # Symbolic id browsing
        #
        # **IMPORTANT:**  Replace these with the *actual* OPC UA node IDs that contain
        # the data you want to collect from the PLC. Inspect the PLC's OPC UA
        # server using a dedicated OPC UA browser (e.g., UAExpert) to identify these node IDs.

        data_node_ids = [
            "ns=3;s=Counter", # Example
            "ns=4;s=TemperatureSensor.Temperature", # Example
            "ns=4;i=1001" # Example
        ]

        # Read data from the specified nodes
        for node_id in data_node_ids:
            try:
                data_node = client.get_node(node_id)
                data_value = data_node.get_value()
                data_name = data_node.get_browse_name().Name  # Get the node's name
                data_type = data_node.get_data_type_as_variant_type()  #Get the datatype

                print(f"Node: {data_name} ({node_id}), Value: {data_value}, Type: {data_type}")


                #  Consider logging the data to a file.  This demonstrates screen output only.
                #  e.g.,  with open("plc_data.txt", "a") as f:
                #           f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {node_id} - {data_value}\n")

            except Exception as e:
                print(f"Error reading node {node_id}: {e}")


    except Exception as e:
        print(f"Error connecting to or communicating with OPC UA server: {e}")
    finally:
        try:
            client.disconnect()
            print("Disconnected from OPC UA server.")
        except:
            pass


if __name__ == "__main__":

    plc_ip = discover_plc_ip()

    if plc_ip:
        collect_plc_data(plc_ip)
    else:
        print("PLC IP address could not be discovered.  Exiting.")


    # Example if PLC IP discovery fails:
    #  Uncomment the following lines ONLY if IP discovery consistently fails and you
    #  have a known, static IP address for the PLC.  Remove the UDP discovery code above in that case.
    # known_plc_ip = "192.168.1.100"  # Replace with the PLC's actual IP address
    # collect_plc_data(known_plc_ip)