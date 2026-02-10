# DISCLAIMER: This code is for educational and research purposes only.
# Do not use it for any malicious activities.  The user is solely
# responsible for any consequences of using this code.  Reverse
# engineering or unauthorized access to industrial control systems
# is illegal and can be dangerous.  Always operate within legal and ethical boundaries.
# This script should only be run in a controlled environment with explicit permission
# from the system owner.

import os
import subprocess
import socket
import time

# Configuration
PLC_VENDOR = "Rockwell Automation" # To find the PLC IP, we'll need vendor information
PLC_MODEL = "Micro850"
ENGINEERING_WORKSTATION_IP = "your_engineering_workstation_ip" #IP address of the computer with the PLC programming software
SAVE_DIRECTORY = "uploaded_programs"
PROGRAM_NAME = "PLC_Program"  #A reasonable default in case it can't be determined dynamically

#  Rockwell software used for program upload.  Requires the software
#  to be installed on the ENGINEERING_WORKSTATION_IP machine and accessible from the command line.
#  These may need to be adjusted based on your specific installation and version.
ROCKWELL_UPLOAD_COMMAND = "RSLinx.exe"  # Example.  Likely needs modification.  RSLogix Micro Starter Lite command line tool will vary.
# Example arguments.  These are highly dependent on the specific upload tool.
#  This is very likely the area needing the most modification.
ROCKWELL_UPLOAD_ARGS = ["-upload", "-port", "Ethernet", "-device", PLC_MODEL, "-file", os.path.join(SAVE_DIRECTORY, f"{PROGRAM_NAME}.acd")]



def find_plc_ip():
    """
    Attempts to discover the PLC IP address on the network.
    This is a simplified example and may require significant modifications
    depending on your network configuration and PLC setup.  A more robust
    discovery mechanism is highly recommended in a real-world scenario.

    This method relies on sending a UDP broadcast and hoping for a response.  This might
    not work on all networks.  Adjust the broadcast message and port as needed.
    """

    # Define the broadcast message and port
    broadcast_message = b"Rockwell Discovery"  # Customize for Micro850 if different
    broadcast_port = 2222 #Default for Rockwell
    timeout_seconds = 5

    # Create a socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout_seconds)

    try:
        # Send the broadcast message
        sock.sendto(broadcast_message, ('<broadcast>', broadcast_port))  # '<broadcast>' is system specific. Might need 255.255.255.255

        # Receive the response (PLC IP address)
        data, addr = sock.recvfrom(1024)
        print(f"Received {len(data)} bytes from {addr}")
        print(f"PLC IP Address: {addr[0]}")
        return addr[0]

    except socket.timeout:
        print("No PLC found within the timeout period.")
        return None
    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None
    finally:
        sock.close()


def check_dependencies():
    """
    Checks for required dependencies, such as RSLinx or other communication tools.
    This is a simplified example and needs to be tailored to your specific environment.
    """
    try:
        # Check if RSLinx is installed (a common dependency)
        subprocess.run([ROCKWELL_UPLOAD_COMMAND, "/?"], capture_output=True, check=True) #The /? flag should return version info if installed.
        print(f"{ROCKWELL_UPLOAD_COMMAND} is installed.")
        return True

    except FileNotFoundError:
        print(f"Error: {ROCKWELL_UPLOAD_COMMAND} not found.  Ensure RSLinx (or equivalent) is installed and in the system path.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error executing {ROCKWELL_UPLOAD_COMMAND}: {e}")
        return False


def upload_plc_program(plc_ip):
    """
    Uploads the PLC program using the specified Rockwell Automation tools.
    This function requires RSLinx or a similar Rockwell communication tool
    to be installed on the ENGINEERING_WORKSTATION_IP.
    """

    if not check_dependencies():
        print("Dependencies not met.  Exiting.")
        return False

    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)

    print(f"Attempting to upload PLC program from {plc_ip}...")

    try:
        # Build the command
        command = [ROCKWELL_UPLOAD_COMMAND] + ROCKWELL_UPLOAD_ARGS
        print(f"Executing: {' '.join(command)}")


        #Execute command on the ENGINEERING_WORKSTATION_IP machine using subprocess or Paramiko (if you need to SSH).
        # This section assumes you are running this script directly on the ENGINEERING_WORKSTATION_IP machine.
        # If you are running this script on a separate Windows machine, you'll need to use Paramiko (SSH) or
        # other remote execution tools to run the command on the ENGINEERING_WORKSTATION_IP.  That adds significant complexity.

        result = subprocess.run(command, capture_output=True, text=True, check=True)  #Add shell=True if necessary.

        if result.returncode == 0:
            print("PLC program uploaded successfully.")
            print(f"Program saved to: {os.path.join(SAVE_DIRECTORY, f'{PROGRAM_NAME}.acd')}")
            return True
        else:
            print("PLC program upload failed.")
            print("Error output:", result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error executing upload command: {e}")
        print("Stderr:", e.stderr)  # Often contains important error messages.
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def main():
    """
    Main function to orchestrate the PLC program upload.
    """

    plc_ip_address = find_plc_ip()

    if plc_ip_address:
        print(f"Using PLC IP Address: {plc_ip_address}")
        success = upload_plc_program(plc_ip_address)
        if success:
            print("Program uploaded successfully.")
        else:
            print("Program upload failed.")
    else:
        print("Could not determine PLC IP address.  Exiting.")

if __name__ == "__main__":
    main()