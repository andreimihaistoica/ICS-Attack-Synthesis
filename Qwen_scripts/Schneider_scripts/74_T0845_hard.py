import nmap
from pycomm3 import LogixDriver
import socket

# Function to find the PLC's IP address
def find_plc_ip(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-p 502')  # Scan for Modbus TCP port (502)
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

# Function to upload the program from the PLC
def upload_program(plc_ip, output_file):
    try:
        with LogixDriver(plc_ip) as plc:
            # Read the program from the PLC
            program = plc.read_program('MainProgram')
            if program:
                with open(output_file, 'w') as file:
                    file.write(program)
                print(f"Program uploaded successfully and saved to {output_file}")
            else:
                print("Failed to read the program from the PLC")
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Define the subnet to scan
    subnet = '192.168.9.0/24'
    
    # Find the PLC's IP address
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        
        # Define the output file for the uploaded program
        output_file = 'uploaded_program.txt'
        
        # Upload the program from the PLC
        upload_program(plc_ip, output_file)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()