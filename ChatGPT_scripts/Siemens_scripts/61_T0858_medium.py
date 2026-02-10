import snap7
from snap7.util import get_int
import time
from scapy.all import ARP, Ether, srp

# Define the network interface and the target IP range (Modify it to match your network)
NETWORK_INTERFACE = "eth0"  # Change according to your system (e.g., "Wi-Fi" on Windows)
IP_RANGE = "192.168.0.1/24"  # Modify this based on your PLC network

def find_plc_ip():
    """Scans the network to find Siemens PLC using ARP requests."""
    print("[*] Scanning network to find Siemens PLC...")

    # Create an ARP request packet
    arp_request = ARP(pdst=IP_RANGE)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    # Send the ARP request and capture responses
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for sent, received in answered_list:
        if received.psrc.startswith("192.168.0."):  # Adjust this filter if needed
            print(f"[+] Potential PLC detected at IP: {received.psrc}")
            return received.psrc  # Return the first found PLC IP

    print("[-] No PLC found on the network.")
    return None

def change_plc_mode(plc_ip, mode):
    """Changes the Siemens PLC's mode (RUN, STOP, etc.)."""
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)  # Connect to the PLC (rack=0, slot=1)

        if mode.lower() == "stop":
            print("[*] Stopping the PLC...")
            plc.plc_stop()
        elif mode.lower() == "run":
            print("[*] Starting the PLC...")
            plc.plc_start()
        else:
            print("[-] Unsupported mode. Use 'RUN' or 'STOP'.")
            return

        time.sleep(2)  # Wait for the mode transition
        plc.disconnect()
        print(f"[+] Successfully changed PLC mode to {mode.upper()}.")

    except Exception as e:
        print(f"[-] Error changing PLC mode: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        change_plc_mode(plc_ip, "STOP")  # Change to "RUN" if needed
    else:
        print("[-] Could not find a PLC. Exiting.")