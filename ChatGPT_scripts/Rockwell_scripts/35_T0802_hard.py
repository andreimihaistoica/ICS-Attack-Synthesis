import scapy.all as scapy
from opcua import Client
import time

# Step 1: Discover the PLC's IP address using ARP scanning
def discover_plc():
    print("[*] Scanning the network to find the PLC...")

    # Define the subnet to scan (Modify based on your network)
    subnet = "192.168.1.1/24"

    # Conduct an ARP scan
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    answered_list = scapy.srp(broadcast/arp_request, timeout=3, verbose=False)[0]

    for sent, received in answered_list:
        print(f"[+] Found Device -> IP: {received.psrc}, MAC: {received.hwsrc}")
        # Assuming Rockwell PLC falls into known MAC vendor ranges
        if "00:1E:F3" in received.hwsrc or "00:80:F4" in received.hwsrc: 
            print(f"[!!] Possible PLC Identified: {received.psrc}")
            return received.psrc
        
    print("[!] No PLC found.")
    return None


# Step 2: Connect to the PLC's OPC UA Server
def collect_plc_data(plc_ip):
    opc_url = f"opc.tcp://{plc_ip}:4840"  # Rockwell Micro850 default OPC UA port
    client = Client(opc_url)
    
    try:
        client.connect()
        print("[*] Connected to PLC OPC UA Server")

        # Retrieve the root node
        root = client.get_root_node()

        # Navigate to the Objects node
        objects = root.get_child(["0:Objects"])

        # Retrieve all PLC tags under "2:PLC"
        plc_tags = objects.get_child(["2:PLC"])

        # Step 3: Enumerate & Collect key process variables
        tags_to_collect = [
            "START", "STOP", "Activate_FanA", "FanA_Timer", "TON_1.Q", 
            "TON_1.ET", "TONOFF_1.IN", "TONOFF_1.Q", "FanA_Off", "Tog_Off"
        ]

        for tag_name in tags_to_collect:
            try:
                node = plc_tags.get_child([f"2:{tag_name}"])
                tag_value = node.get_value()
                print(f"[COLLECTION] {tag_name}: {tag_value}")
            except Exception as e:
                print(f"[ERROR] Failed to read {tag_name}: {str(e)}")

        client.disconnect()
        print("[*] Disconnected from PLC OPC UA Server")

    except Exception as e:
        print(f"[ERROR] OPC UA Connection Failed: {str(e)}")


# Main Execution Flow
if __name__ == "__main__":
    plc_ip = discover_plc()
    
    if plc_ip:
        collect_plc_data(plc_ip)
    else:
        print("[!] Exiting: PLC could not be identified.")