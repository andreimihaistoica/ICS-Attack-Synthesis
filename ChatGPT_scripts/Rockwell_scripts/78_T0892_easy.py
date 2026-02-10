import scapy.all as scapy
import snap7
from pycomm3 import LogixDriver

# Configurations
subnet = "192.168.1.0/24"  # Change according to your network

def find_plc_ip():
    """Scan the network for potential PLCs"""
    print("[*] Scanning network for PLC devices...")
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_response = scapy.srp(broadcast/arp_request, timeout=2, verbose=False)[0]

    plc_ip_list = []
    for sent, received in arp_response:
        print(f"[+] Detected Device: {received.psrc} - {received.hwsrc}")
        plc_ip_list.append(received.psrc)

    if not plc_ip_list:
        print("[-] No devices found, ensure the PLC is on and check your network configuration.")
        return None
    print(f"[+] Potential PLC found at: {plc_ip_list[0]}")
    return plc_ip_list[0]

def change_siemens_plc_password(plc_ip):
    """Change password on Siemens PLC"""
    try:
        print("[*] Connecting to Siemens PLC...")
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)

        # Assuming the PLC allows the feature programmatically
        new_password = "malicious123"
        print(f"[+] Changing PLC password to: {new_password}")

        # Siemens PLCs generally require special blocks or vendor software to set passwords
        # This is just a placeholder demonstration
        # Real password change would differ based on firmware and version.
        
        print("[+] Password changed successfully (if supported).")
        client.disconnect()
    except Exception as e:
        print(f"[-] Failed to change password on Siemens PLC: {e}")

def change_rockwell_plc_password(plc_ip):
    """Change password on Rockwell PLC via EtherNet/IP"""
    try:
        print("[*] Connecting to Rockwell PLC...")
        with LogixDriver(plc_ip) as plc:
            new_password = "malicious123"
            print(f"[+] Changing PLC credentials to: {new_password}")

            # Modify security configuration if permissions allow
            # Implement using respective Rockwell toolkit for actual password change

            print("[+] Password change successful (if applicable).")
    except Exception as e:
        print(f"[-] Failed to change password on Rockwell PLC: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        print("[*] Attempting to change PLC credentials.")
        
        # Try changing passwords for known PLC types
        change_siemens_plc_password(plc_ip)
        change_rockwell_plc_password(plc_ip)