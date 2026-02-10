import socket
from scapy.all import ARP, Ether, srp
from pylogix import PLC

# Rockwell/Allen-Bradley Micro850 PLC Default Credentials
DEFAULT_USERNAME = "admin"  # Example default username
DEFAULT_PASSWORD = "password"  # Example default password

# Network settings (modify this for your network range)
NETWORK_RANGE = "192.168.1.0/24"  # Example subnet range

def discover_plc_ip():
    """
    Discover the Rockwell Micro850 PLC IP address using ARP request.
    """
    print("[*] Scanning network to find Rockwell Micro850 PLC...")

    # Broadcast ARP request
    ans, _ = srp(
        Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=NETWORK_RANGE),
        timeout=2,
        verbose=False
    )

    for sent, received in ans:
        ip_address = received.psrc
        mac_address = received.hwsrc

        # Check if the MAC vendor is Rockwell (00:00:BC prefix typically used)
        if mac_address.startswith("00:00:BC"):
            print(f"[+] Found Rockwell Micro850 PLC at {ip_address} ({mac_address})")
            return ip_address

    print("[-] No Rockwell PLC found on the network.")
    return None

def attempt_default_login(plc_ip):
    """
    Try logging into the PLC using default credentials.
    """
    print(f"[*] Attempting login to PLC at {plc_ip} using default credentials...")

    try:
        plc = PLC()
        plc.IPAddress = plc_ip

        # Attempt to read a tag to verify authentication success
        response = plc.Read("System")  # Trying to read a system tag

        if response.Status == "Success":
            print("[+] Successfully authenticated using default credentials!")
            print("[+] PLC is accessible and may be vulnerable.")
        else:
            print("[-] Authentication failed. Default credentials do not work.")
        
        plc.Close()
    except Exception as e:
        print(f"[!] Error communicating with PLC: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        attempt_default_login(plc_ip)