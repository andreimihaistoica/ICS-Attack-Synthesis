from pylogix import PLC
from scapy.all import ARP, Ether, srp
import time

# Network scanner - Finds PLC IP by looking for EtherNet/IP devices
def find_plc_ip(interface="eth0", timeout=5):
    print("[*] Scanning network for PLC...")

    # Define the ARP request
    arp = ARP(pdst="192.168.1.1/24")  # Adjust network range as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and capture the response
    answered, _ = srp(packet, timeout=timeout, iface=interface, verbose=False)
    
    for sent, received in answered:
        if "Rockwell Automation" in received.hwsrc:  # Checking hardware vendor may help identify PLC
            print(f"[+] Found Rockwell PLC at {received.psrc}")
            return received.psrc

    print("[-] No PLC found on the network.")
    return None

# Change the operating mode of the Micro850
def change_plc_mode(plc_ip, mode="Program"):
    mode_map = {
        "Program": 0,
        "Run": 1,
        "Stop": 2,
        "Test": 3
    }
    
    if mode not in mode_map:
        print(f"[-] Invalid mode: {mode}")
        return False

    print(f"[*] Connecting to PLC at {plc_ip}...")
    
    # Connect to Micro850 PLC using pylogix
    plc = PLC()
    plc.IPAddress = plc_ip

    # Send command to change mode
    response = plc.SetControllerMode(mode_map[mode])
    
    if response.Status == 'Success':
        print(f"[+] Successfully changed PLC mode to: {mode}")
    else:
        print(f"[-] Failed to change PLC mode: {response.Status}")

    plc.Close()

if __name__ == "__main__":
    # Step 1: Find the PLC IP address
    plc_ip = find_plc_ip()
    
    if not plc_ip:
        print("[-] Exiting - No PLC found.")
    else:
        # Step 2: Change the PLC operating mode
        target_mode = "Program"  # Change to "Run", "Stop", etc., as needed
        change_plc_mode(plc_ip, target_mode)