from cpppo.server.enip import client
import socket
import time

# Define the IP address of the PLC
plc_ip = None

# Function to find the PLC's IP address if it's not known
def find_plc_ip():
    # This could involve scanning the network or using a discovery protocol
    # For simplicity, let's assume you have a list of potential IPs
    potential_ips = ['192.168.1.1', '192.168.1.2']
    for ip in potential_ips:
        # Send a discovery packet and check for a response
        # This step is highly dependent on the specific protocol and device
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to upload a program from the PLC
def upload_program():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the program to upload
            program_name = 'Prog1'
            
            # Upload the program from the PLC
            # The specific commands to upload a program may vary depending on the PLC model and firmware
            program_data = conn.read([program_name])
            print("Program uploaded from PLC")
            
            # Save the program data to a file
            with open('program_data.txt', 'w') as f:
                f.write(str(program_data))
            print("Program data saved to file")
    else:
        print("PLC IP address not found")

# Function to read a program from the PLC using vendor software
def read_program_vendor_software():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the program to read
            program_name = 'Prog1'
            
            # Read the program from the PLC using vendor software
            # The specific commands to read a program may vary depending on the PLC model and firmware
            program_data = conn.read([program_name])
            print("Program read from PLC using vendor software")
            
            # Save the program data to a file
            with open('program_data_vendor_software.txt', 'w') as f:
                f.write(str(program_data))
            print("Program data saved to file")
    else:
        print("PLC IP address not found")

# Function to upload a program to a workstation or jump box
def upload_program_workstation():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the program to upload
            program_name = 'Prog1'
            
            # Upload the program to a workstation or jump box
            # The specific commands to upload a program may vary depending on the PLC model and firmware
            program_data = conn.read([program_name])
            print("Program uploaded to workstation or jump box")
            
            # Save the program data to a file
            with open('program_data_workstation.txt', 'w') as f:
                f.write(str(program_data))
            print("Program data saved to file")
    else:
        print("PLC IP address not found")

# Main function to start the collection
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Upload a program from the PLC
        upload_program()
        
        # Read a program from the PLC using vendor software
        read_program_vendor_software()
        
        # Upload a program to a workstation or jump box
        upload_program_workstation()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()