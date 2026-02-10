import sys
from opcua import Client
from scapy.all import ARP, Ether, srp

# Function to discover the PLC IP address using ARP scanning
def discover_plc_ip(network="192.168.1.0/24"):  # Change based on your network
    print(f"[*] Scanning for PLC on {network} ...")
    arp_request = ARP(pdst=network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        if "Siemens" in received.hwsrc or "Rockwell" in received.hwsrc:  # Modify based on vendor MAC prefix
            print(f"[+] PLC Found: {received.psrc} ({received.hwsrc})")
            return received.psrc  # Return PLC IP address

    print("[-] No PLC Found!")
    sys.exit(1)

# Function to connect to the PLC via OPC UA and enumerate available nodes
def collect_opc_ua_data(plc_ip):
    url = f"opc.tcp://{plc_ip}:4840"  # Default OPC UA port 4840
    print(f"[*] Connecting to OPC UA Server at {url}")

    try:
        client = Client(url)
        client.connect()
        print("[+] Connected successfully!")

        # Get the root node
        root = client.get_root_node()
        print(f"[*] Root Node: {root}")

        # Browse Objects folder
        objects = root.get_child(["0:Objects"])
        print("[*] Available Nodes Under Objects:")
        for node in objects.get_children():
            print(f"  - {node} ({node.get_browse_name()})")

        # Get some process values if available (Example: Machine Temperature if it exists)
        try:
            temp_node = client.get_node("ns=2;s=MachineTemperature")  # Modify based on actual node ID
            temperature = temp_node.get_value()
            print(f"[+] Machine Temperature: {temperature} °C")
        except Exception as e:
            print(f"[-] Could not retrieve temperature: {e}")

        client.disconnect()
    except Exception as e:
        print(f"[-] Failed to connect to OPC UA Server: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()  # Discover the PLC IP dynamically
    collect_opc_ua_data(plc_ip)  # Connect and gather data

if __name__ == "__main__":
    main()