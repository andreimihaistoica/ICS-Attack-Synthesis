import opcua
import socket
import subprocess
import re
import time

# Configuration
OPCUA_SERVER_ENDPOINT = "opc.tcp://{}:4840/freeopcua/server/".format("PLC_IP")  # Placeholder, will be replaced
OUTPUT_FILE = "collected_data.txt"
MAX_RETRIES_PLC_DISCOVERY = 3
RETRY_DELAY_PLC_DISCOVERY = 5  # Seconds

# Helper function to run commands and capture output
def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return None

# Function to discover the PLC's IP address.  This attempts several methods.
def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address using several methods:
    1. ARP table:  Looks for a device with a known MAC address prefix
    2. nmap scan of the local network (requires nmap installed)
    3.  Attempts to connect to a range of common PLC IPs.

    Returns: The IP address if found, None otherwise.
    """

    print("Attempting to discover the PLC's IP address...")

    # Method 1: ARP table scan (Least reliable but fast and doesn't require external tools)
    print("Trying ARP table scan...")
    for attempt in range(MAX_RETRIES_PLC_DISCOVERY):
        try:
            arp_output = run_command(["arp", "-a"])
            if arp_output:
                for line in arp_output.splitlines():
                    if "PLC_MAC_PREFIX" in line:  # Replace "PLC_MAC_PREFIX" with a portion of the PLC's MAC address
                        ip_address = line.split()[1].strip("()")
                        print(f"Found PLC IP in ARP table: {ip_address}")
                        return ip_address
            print(f"ARP scan failed, attempt {attempt+1}.  Retrying in {RETRY_DELAY_PLC_DISCOVERY} seconds...")
            time.sleep(RETRY_DELAY_PLC_DISCOVERY)


        except Exception as e:
            print(f"Error during ARP scan: {e}")


    # Method 2: nmap scan (More reliable, requires nmap)
    print("Trying nmap scan (requires nmap installed)...")
    try:
        # Find the network interface
        ip_route_output = run_command(["ip", "route"])
        if ip_route_output:
            default_route = next((line for line in ip_route_output.splitlines() if "default" in line), None)
            if default_route:
                interface = default_route.split("dev")[1].split()[0].strip()
                # Get the network address
                ip_address_output = run_command(["ip", "addr", "show", interface])
                if ip_address_output:
                    network_address = re.search(r"inet\s([^\/]+)", ip_address_output)
                    if network_address:
                        network_address = network_address.group(1).strip()
                        # Convert the network address to the network subnet for nmap scan
                        network_subnet = ".".join(network_address.split(".")[:-1]) + ".0/24"

                        for attempt in range(MAX_RETRIES_PLC_DISCOVERY):
                            try:
                                nmap_output = run_command(["nmap", "-sn", network_subnet])  # Simple ping scan
                                if nmap_output:
                                    # Try to find the PLC by known port/service
                                    ip_matches = re.findall(r"Nmap scan report for (.*)", nmap_output) # find all hosts responding
                                    if ip_matches:
                                        for ip in ip_matches:
                                            try:
                                                # Attempt connection on OPCUA port.
                                                client = opcua.Client(f"opc.tcp://{ip}:4840/freeopcua/server/")
                                                client.connect()
                                                print(f"Found PLC IP through OPCUA on: {ip}")
                                                client.disconnect()
                                                return ip

                                            except Exception as connect_err:
                                                print(f"Failed OPCUA connection to {ip}: {connect_err}")
                                                pass # try next IP

                                    print(f"nmap scan did not find a likely PLC on {network_subnet}, attempt {attempt+1}. Retrying in {RETRY_DELAY_PLC_DISCOVERY} seconds...")
                                    time.sleep(RETRY_DELAY_PLC_DISCOVERY)

                            except Exception as e:
                                print(f"Error during nmap scan: {e}")
                                print(f"nmap scan failed, attempt {attempt+1}. Retrying in {RETRY_DELAY_PLC_DISCOVERY} seconds...")
                                time.sleep(RETRY_DELAY_PLC_DISCOVERY)




            else:
                print("Could not determine network interface from 'ip route' command output.")
        else:
            print("Could not determine network interface using 'ip route' command.")


    except FileNotFoundError:
        print("nmap is not installed.  Please install nmap to use this discovery method.")
    except Exception as e:
        print(f"Error during nmap execution: {e}")

    # Method 3:  Attempt to connect to common PLC IPs (dangerous, but last resort)
    print("Trying common PLC IP addresses (last resort and potentially dangerous)...")
    common_plc_ips = ["192.168.1.10", "192.168.0.10", "10.0.0.10", "192.168.1.100"] # Add more as needed.  Use ONLY internal networks.

    for ip in common_plc_ips:
        try:
            client = opcua.Client(f"opc.tcp://{ip}:4840/freeopcua/server/")
            client.connect()
            print(f"Successfully connected to PLC at: {ip}")
            client.disconnect()
            return ip
        except Exception as e:
            print(f"Failed to connect to {ip}: {e}")


    print("PLC IP address discovery failed.")
    return None


# Main function
def main():

    plc_ip = discover_plc_ip()

    if not plc_ip:
        print("Could not determine PLC IP address. Exiting.")
        return

    opcua_server_endpoint = "opc.tcp://{}:4840/freeopcua/server/".format(plc_ip)

    try:
        client = opcua.Client(opcua_server_endpoint)
        client.connect()

        print(f"Connected to OPC UA server at: {opcua_server_endpoint}")


        # Get root node
        root = client.get_root_node()

        # Function to recursively collect data from nodes
        def collect_data(node, indent=""):
            node_id = node.nodeid.to_string()
            node_name = node.get_browse_name().to_string()
            node_class = node.get_node_class().name
            data_type = ""
            value = ""

            try:
                if node_class == "Variable":
                    data_type = node.get_data_type_as_variant_type().name
                    value = node.get_value()
                    if isinstance(value, bytes):
                      value = "Bytes Data" # avoid long byte strings in output
                    else:
                      value = str(value) # cast to string for consistency
                else:
                  value = "N/A"

            except Exception as e:
                value = f"Error getting value: {e}"


            with open(OUTPUT_FILE, "a") as f:
                f.write(f"{indent}Node ID: {node_id}\n")
                f.write(f"{indent}Node Name: {node_name}\n")
                f.write(f"{indent}Node Class: {node_class}\n")
                f.write(f"{indent}Data Type: {data_type}\n")
                f.write(f"{indent}Value: {value}\n")
                f.write(f"{indent}------------------------------\n")

            # Recursively collect data from children
            for child in node.get_children():
                collect_data(child, indent + "  ")

        # Start collecting data from the root node
        with open(OUTPUT_FILE, "w") as f:  # Clear the file before writing
            f.write("Starting OPC UA Data Collection:\n")
        collect_data(root)

        print(f"Data collected and saved to: {OUTPUT_FILE}")

    except opcua.ua.uaerrors.BadServerUriInvalid as e:
        print(f"Error: Invalid OPC UA server URI. Please check the OPCUA_SERVER_ENDPOINT.  Error details: {e}")
    except ConnectionRefusedError as e:
        print(f"Error: Connection refused.  Make sure the OPC UA server is running and accessible on {opcua_server_endpoint}. Error details: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        try:
            client.disconnect()
        except:
            pass

if __name__ == "__main__":
    main()