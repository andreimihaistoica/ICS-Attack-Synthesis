import sys
import time
import logging
from opcua import Client
import nmap
from scapy.all import ARP, Ether, srp
import netifaces as ni

# Configure logging
logging.basicConfig(filename="plc_data.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Function to get local network IP range
def get_local_ip_range():
    iface = ni.gateways()["default"][ni.AF_INET][1]  # Get default network interface
    ip_info = ni.ifaddresses(iface)[ni.AF_INET][0]["addr"]
    subnet_mask = ni.ifaddresses(iface)[ni.AF_INET][0]["netmask"]
    
    # Convert to CIDR format
    cidr_suffix = sum(bin(int(x)).count("1") for x in subnet_mask.split("."))
    return f"{ip_info}/{cidr_suffix}"

# Function to scan the network for Siemens PLCs using ARP/Nmap
def find_plc_ip():
    local_network = get_local_ip_range()
    
    print(f"Scanning network {local_network} for Siemens PLC...")
    nm = nmap.PortScanner()
    nm.scan(hosts=local_network, arguments="-p 4840 --open")  # 4840 is OPC UA port

    for host in nm.all_hosts():
        print(f"Found potential PLC at {host}")
        return host  # Returning first found IP
    return None

# Function to connect to OPC UA server on PLC
def connect_opcua(plc_ip):
    opc_url = f"opc.tcp://{plc_ip}:4840"
    print(f"Connecting to OPC UA Server: {opc_url}...")
    
    try:
        client = Client(opc_url)
        client.connect()
        print("[+] Successfully connected to OPC UA server.")
        return client
    except Exception as e:
        print(f"[-] Unable to connect to OPC UA server: {e}")
        return None

# Function to fetch all available tags from OPC UA server
def collect_plc_data(client):
    try:
        root = client.get_root_node()
        objects = client.get_objects_node()
        print("[+] Fetching PLC data...")
        
        # Assuming Siemens OPC nodes follow "Objects/PLC" structure
        variables = objects.get_children()
        for var in variables:
            try:
                tag_name = var.get_display_name().Text
                tag_value = var.get_value()
                print(f"{tag_name}: {tag_value}")
                logging.info(f"{tag_name}: {tag_value}")
            except:
                continue
    except Exception as e:
        print(f"[-] Error collecting data: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    
    if not plc_ip:
        print("[-] No Siemens PLC found on the network.")
        return

    client = connect_opcua(plc_ip)

    if client:
        collect_plc_data(client)
        client.disconnect()
        print("[+] Data collection complete.")

if __name__ == "__main__":
    main()