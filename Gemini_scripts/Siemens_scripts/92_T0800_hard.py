import snap7
import time
import subprocess
import re

# Configuration -  Adjust these based on your actual setup
PLC_RACK = 0
PLC_SLOT = 1
FIRMWARE_UPDATE_MODE_ADDRESS = '%M0.6' #  Example Memory bit, likely different for your specific PLC & function block
ENGINEERING_STATION_IP = "192.168.1.100"  # Replace with the actual IP of your Engineering Station
PLC_DEFAULT_IP = "192.168.1.1" #Default PLC IP to try if network scan fails

# Function to determine the PLC IP address by scanning the network
def get_plc_ip_address(engineering_station_ip):
    """
    Attempts to discover the PLC IP address by analyzing the ARP table of the engineering station.
    Relies on the assumption that the engineering station has recently communicated with the PLC.
    """
    try:
        # Execute the arp -a command on the engineering station.  Requires psexec or similar remote execution capability
        # The following command assumes psexec is in the PATH
        command = f'psexec \\\\{engineering_station_ip} -u "domain\\user" -p "password" arp -a' #Replace domain\\user and password with valid credentials for the remote machine.
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error executing arp -a on {engineering_station_ip}: {result.stderr}")
            return None

        arp_output = result.stdout

        # Parse the ARP output to find an IP address that looks like a PLC IP
        #  This is a very simple heuristic.  Improve as needed
        for line in arp_output.splitlines():
            if PLC_DEFAULT_IP[:7] in line:  #Check to see if the PLC_Default_IP prefix is present
                ip_address = line.split()[0]
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address): #Validate as IP address
                    return ip_address

        print("PLC IP address not found in ARP table.  Using default")
        return PLC_DEFAULT_IP #Fallback to the default IP
    except FileNotFoundError:
        print("Error: psexec not found. Ensure it's in your system's PATH or specify the full path.")
        return None
    except Exception as e:
        print(f"An error occurred during IP discovery: {e}")
        return None



# Function to toggle the firmware update mode bit
def toggle_firmware_update_mode(plc_ip,firmware_update_address):
    """
    Toggles the firmware update mode bit on the PLC.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)

        # Determine the byte and bit offset from the address string.  This is very basic parsing.
        match = re.match(r"%M(\d+)\.(\d+)", firmware_update_address)
        if not match:
           raise ValueError(f"Invalid address format: {firmware_update_address}")

        byte_address = int(match.group(1)) // 8
        bit_offset = int(match.group(2))
        offset_within_byte = int(match.group(1)) % 8

        # Read the byte containing the bit we want to flip
        read_data = plc.read_area(snap7.const.Areas.MK, 0, byte_address, 1)

        original_byte = read_data[0]

        # Toggle the specified bit
        new_byte = original_byte ^ (1 << bit_offset) #Corrected bitwise shift

        # Write the modified byte back to the PLC
        write_data = bytearray([new_byte])  # Convert to bytearray
        plc.write_area(snap7.const.Areas.MK, 0, byte_address, write_data)


        plc.disconnect()
        print(f"Successfully toggled firmware update mode bit at {firmware_update_address} on PLC {plc_ip}.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'plc' in locals():
            try:
                plc.disconnect()
            except:
                pass


if __name__ == "__main__":
    plc_ip = get_plc_ip_address(ENGINEERING_STATION_IP)

    if plc_ip:
        print(f"PLC IP address: {plc_ip}")
    else:
        print("Failed to determine PLC IP address.  Exiting.")
        exit()


    # Step 1: Activate Firmware Update Mode
    print("Attempting to activate firmware update mode...")
    toggle_firmware_update_mode(plc_ip,FIRMWARE_UPDATE_MODE_ADDRESS)
    time.sleep(5)  # Give the PLC some time to process

    # Step 2: Deactivate Firmware Update Mode (after a delay)
    print("Attempting to deactivate firmware update mode...")
    toggle_firmware_update_mode(plc_ip,FIRMWARE_UPDATE_MODE_ADDRESS)
    print("Done.")