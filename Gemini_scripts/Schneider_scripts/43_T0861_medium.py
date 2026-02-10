import snap7
import socket
import struct
import re
import time

# MITRE ATT&CK Technique: Collection - Point & Tag Identification (T1647)

# Configuration - Adjust these values based on your specific setup

PLC_IP = None  # Initially unknown, will be discovered
PLC_RACK = 0   # Usually 0 for TM221CE16R
PLC_SLOT = 1   # Usually 1 for TM221CE16R

# --- IP Address Discovery Function ---
def discover_plc_ip():
    """
    Discovers the PLC's IP address on the local network using a broadcast.
    This is a basic approach and might need adjustments depending on the network configuration.
    """
    broadcast_address = '<broadcast>' # Send the broadcast address.
    port = 12345  # Choose a port for broadcasting.  Needs to match the expected PLC response port (if any).  This is a common, unused port.
    message = b"DiscoverPLC" # Simple discovery message. Can be anything.

    # Create a UDP socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Timeout after 5 seconds

    try:
        sock.sendto(message, (broadcast_address, port))
        print("Broadcast message sent. Waiting for PLC response...")

        data, addr = sock.recvfrom(1024)  # Buffer size
        print("Received response from:", addr)
        decoded_data = data.decode('utf-8', 'ignore')  # Decode data, ignoring errors
        print("Data received:", decoded_data)  # Added decoded data print for debugging
        sock.close()

        # Attempt to extract the IP address from the response.
        #  This assumes the PLC sends its IP in the response.
        # Adjust the regex pattern as needed based on the PLC's response format.
        match = re.search(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', decoded_data)

        if match:
            return match.group(0)
        else:
            print("No IP address found in the PLC response.  Check PLC's response and adjust regex.")
            return None

    except socket.timeout:
        print("No response received from the PLC within the timeout period.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None
    finally:
        sock.close()



# --- Tag/Point Extraction Functions ---

def extract_tags_from_plc(plc_ip, rack, slot):
    """
    Simulates tag/point extraction from the PLC.

    In a real attack, this function would actively retrieve tag and point information
    from the PLC using libraries or protocols like Snap7, Modbus, OPC, etc.
    Since directly accessing a TM221CE16R PLC's tag/symbol table without specific vendor-provided tools
    or reverse engineering is complex, this example simulates the process.

    Args:
        plc_ip (str): IP address of the PLC.
        rack (int): PLC rack number.
        slot (int): PLC slot number.

    Returns:
        dict: A dictionary representing the extracted tags and their associated point information.
              Returns None if an error occurs.
    """

    try:
        # *** REAL IMPLEMENTATION WOULD GO HERE ***

        # In a real-world scenario, you would use a library like Snap7 or Modbus to connect
        # to the PLC and extract the symbol table or relevant data blocks.  This is *highly*
        # PLC specific and requires knowledge of the PLC's protocol and memory layout.

        # For example (using Snap7 - requires installation: pip install python-snap7):
        # client = snap7.client.Client()
        # client.connect(plc_ip, rack, slot)
        # db_number = 1  # Example: Data Block number
        # start_address = 0 # Example: Starting address
        # size = 100 # Example: Number of bytes to read
        # data = client.db_read(db_number, start_address, size)
        # client.disconnect()

        # The 'data' variable would then need to be parsed based on the PLC's data types
        # to extract meaningful tag/point values.  This parsing is *highly* PLC-specific.

        # *** SIMULATED DATA FOR DEMONSTRATION ***
        print("Simulating tag/point extraction from PLC...")
        time.sleep(2) # Simulate network activity

        simulated_tags = {
            "Motor1_Speed": {"address": "%MW0", "type": "INT", "description": "Speed of Motor 1 (RPM)"},
            "Tank1_Level": {"address": "%MD4", "type": "REAL", "description": "Level of Tank 1 (meters)"},
            "Valve2_State": {"address": "%QX0.0", "type": "BOOL", "description": "State of Valve 2 (Open/Closed)"},
            "Temperature_SP": {"address": "%MD8", "type": "REAL", "description": "Temperature Setpoint (degrees C)"},
            "Pressure_PV": {"address": "%MD12", "type": "REAL", "description": "Pressure Process Variable (PSI)"}
        }

        print("Simulated tag/point extraction complete.")
        return simulated_tags

    except Exception as e:
        print(f"Error extracting tags from PLC: {e}")
        return None


def save_tags_to_file(tags, filename="extracted_tags.txt"):
    """
    Saves the extracted tags to a file.

    Args:
        tags (dict): Dictionary of extracted tags.
        filename (str): Name of the file to save the tags to.
    """
    try:
        with open(filename, "w") as f:
            f.write("Extracted Tags and Points:\n")
            for tag, details in tags.items():
                f.write(f"  Tag: {tag}\n")
                for key, value in details.items():
                    f.write(f"    {key}: {value}\n")
                f.write("\n")
        print(f"Tags saved to {filename}")
    except Exception as e:
        print(f"Error saving tags to file: {e}")


# --- Main Script ---

if __name__ == "__main__":
    # 1. Discover PLC IP Address
    print("Discovering PLC IP address...")
    PLC_IP = discover_plc_ip()

    if PLC_IP:
        print(f"PLC IP address found: {PLC_IP}")

        # 2. Extract Tags from PLC
        extracted_tags = extract_tags_from_plc(PLC_IP, PLC_RACK, PLC_SLOT)

        if extracted_tags:
            # 3. Save Tags to File
            save_tags_to_file(extracted_tags)
        else:
            print("Failed to extract tags from PLC.")
    else:
        print("Failed to discover PLC IP address.  Ensure PLC is on the network and responding to broadcasts.")