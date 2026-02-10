import nmap
import pycomm3

def find_plc_ip():
    # Initialize the nmap scanner
    nm = nmap.PortScanner()
    
    # Scan the network for open ports (PLC typically uses port 44818 for Allen Bradley or 102 for Siemens)
    nm.scan(hosts='192.168.1.0/24', arguments='-p 44818,102 --open')
    
    # Iterate through the scan results to find the PLC's IP
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            print(f"Found PLC at IP: {host}")
            return host
    print("PLC not found on the network.")
    return None

def modify_plc_program(plc_ip):
    try:
        # Connect to the PLC (Allen Bradley example using pycomm3)
        with pycomm3.LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")
            
            # Example: Modify a program by writing to a specific tag
            plc.write('MyTag', 12345)
            print("Program modified successfully.")
            
            # Example: Add new logic (this is highly PLC-specific and may require custom logic)
            # plc.write('NewTag', 67890)
            # print("New logic added successfully.")
    
    except Exception as e:
        print(f"Failed to modify PLC program: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Modify the PLC's program
        modify_plc_program(plc_ip)
    else:
        print("PLC IP address not found. Exiting.")