import pycomm3
import nmap

# Function to find the PLC's IP address
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 44818')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if '44818/tcp' in nm[host]['tcp'] and nm[host]['tcp'][44818]['state'] == 'open':
            return host
    return None

# Function to modify the PLC program
def modify_plc_program(plc_ip):
    try:
        with pycomm3.CipDriver(plc_ip) as driver:
            if driver.open():
                print(f"Connected to PLC at {plc_ip}")

                # Define the new function or modification
                new_function = """
                FUNCTION NewFunction : BOOL
                    // New function logic
                    NewFunction := TRUE;
                END_FUNCTION
                """

                # Add the new function to the PLC
                driver.write_tag('NewFunction', new_function)

                # Modify an existing function or logic
                modified_logic = """
                // Rung 8 - New persistent logic
                IF NewFunction() THEN
                    _IO_EM_DO_08 := TRUE;  // New output
                ELSE
                    _IO_EM_DO_08 := FALSE;
                END_IF;
                """

                # Append the modified logic to the existing program
                driver.write_tag('Prog1', modified_logic)

                print("Program modified successfully.")
            else:
                print("Failed to connect to the PLC.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        modify_plc_program(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()