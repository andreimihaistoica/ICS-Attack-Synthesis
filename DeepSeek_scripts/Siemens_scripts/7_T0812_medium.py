import snap7
import nmap
import sys

# Default credentials for Siemens S7-1200 PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "default_password"  # Replace with actual default password

def find_plc_ip():
    # Initialize the nmap scanner
    nm = nmap.PortScanner()
    
    # Scan the local network for open TCP port 102 (S7 communication port)
    nm.scan(hosts='192.168.1.0/24', arguments='-p 102 --open')
    
    # Iterate through the scan results to find the PLC's IP address
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and 102 in nm[host]['tcp'] and nm[host]['tcp'][102]['state'] == 'open':
            print(f"PLC found at IP: {host}")
            return host
    
    print("PLC not found on the network.")
    return None

def connect_to_plc(ip):
    try:
        # Create a PLC object
        plc = snap7.client.Client()
        
        # Attempt to connect using default credentials
        plc.connect(ip, 0, 1)  # IP, rack, slot
        
        if plc.get_connected():
            print("Successfully connected to the PLC using default credentials!")
            # Perform any further actions here (e.g., read/write data)
        else:
            print("Failed to connect to the PLC.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Disconnect from the PLC
        plc.disconnect()

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Attempt to connect to the PLC using default credentials
        connect_to_plc(plc_ip)
    else:
        print("Exiting script.")

if __name__ == "__main__":
    main()