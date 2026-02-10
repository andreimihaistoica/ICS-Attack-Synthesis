import time
from scapy.all import ARP, Ether, srp
from pycomm3 import LogixDriver

# Network settings (Ensure you are scanning the correct network)
NETWORK_IP_RANGE = "192.168.1.0/24"  # Adjust based on your network

def find_plc_ip():
    """
    Scan the network to find the PLC's IP address by identifying Rockwell signature.
    """
    print("[*] Scanning network for PLC...")
    
    # Create an ARP request packet
    arp_request = ARP(pdst=NETWORK_IP_RANGE)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    # Send the packet and collect valid responses
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for sent, received in answered_list:
        if "Rockwell Automation" in received.summary():
            print(f"[+] PLC Found: {received.psrc}")
            return received.psrc
    
    print("[-] No PLC found on the network.")
    return None

def restart_plc(plc_ip):
    """
    Send a restart command to the Rockwell Micro850 PLC.
    """
    print(f"[*] Attempting to restart PLC at {plc_ip}...")

    try:
        with LogixDriver(plc_ip) as plc:
            plc.write("PROGRAM:MainProgram.RUN", 0)  # Stop the PLC
            time.sleep(2)  # Wait before restarting
            plc.write("PROGRAM:MainProgram.RUN", 1)  # Start the PLC

        print("[+] PLC Restart Command Sent Successfully.")

    except Exception as e:
        print(f"[-] Failed to restart PLC: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:  # If PLC is found, restart it
        restart_plc(plc_ip)
    else:
        print("[-] No PLC found. Exiting.")