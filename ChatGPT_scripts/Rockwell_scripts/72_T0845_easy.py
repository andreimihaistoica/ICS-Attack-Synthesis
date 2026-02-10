import snap7
import socket
import struct
import subprocess

def find_plc_ip():
    """
    Identify the PLC IP address by scanning the local subnet.
    Assumes the PLC responds to ARP or is discoverable on the network.
    """
    discovered_ips = []
    
    # Run an nmap scan if available (Linux/macOS/Windows with nmap installed)
    try:
        output = subprocess.check_output("nmap -p 102 --open -oG - 192.168.1.0/24", shell=True).decode()
        for line in output.split("\n"):
            if "open" in line:
                discovered_ips.append(line.split(" ")[1])  # Extract the IP
    except Exception as e:
        print(f"Nmap Scan Failed: {e}")

    if discovered_ips:
        print(f"Possible PLC IPs found: {discovered_ips}")
        return discovered_ips[0]  # Assume the first found IP is PLC
    else:
        print("No PLCs found.")
        return None


def upload_plc_program(plc_ip):
    """
    Connects to a Siemens S7 PLC, attempts to read the memory to gather logic (Program Upload).
    Uses S7comm protocol via snap7.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)  # Connects to PLC (rack=0, slot=1 for common setup)
        print(f"Connected to PLC at {plc_ip}")

        # Attempt to read memory area where logic is stored
        # Assumes access to a DB (Data Block) where logic may be stored
        db_number = 1
        size = 256  # Reading 256 bytes from DB1
        logic_data = plc.db_read(db_number, 0, size)

        print(f"Program Data Retrieved (First 20 bytes): {logic_data[:20]}")
        # Save to a local file for analysis
        with open('plc_program_backup.bin', 'wb') as f:
            f.write(logic_data)

        print("PLC program uploaded and saved as 'plc_program_backup.bin'")
        plc.disconnect()
    except Exception as e:
        print(f"Failed to upload program from PLC: {e}")

if __name__ == "__main__":
    print("[*] Searching for PLC on the network...")
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"[*] Found PLC at {plc_ip}. Attempting to upload its program...")
        upload_plc_program(plc_ip)
    else:
        print("[!] No PLC found, terminating script.")