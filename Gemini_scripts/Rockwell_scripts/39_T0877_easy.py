# MITRE ATT&CK Technique T0819: Collection - I/O Image

# This script attempts to collect the I/O Image state of a PLC 
# using a Native API approach.  It leverages a hypothetical PLC library.

# NOTE: This script requires a PLC communication library (replace 'plc_lib' with the actual library).
#  This example assumes the library provides functions for:
#   - discovering PLCs on the network
#   - connecting to a PLC
#   - reading the I/O Image data
#   - handling errors
#
#  This is a simplified example for demonstration purposes and 
#  may require modifications based on the specific PLC and library used.
#  Error handling and security considerations should be enhanced in a production environment.

import plc_lib  # Replace with the actual PLC library
import socket

# Configuration
# If PLC IP is unknown, set PLC_IP to None.  The script will attempt to discover it.
PLC_IP = None  # Replace with the known IP address if available.
# You may need to find out the proper port through a separate discovery operation, but many plcs use 502 so this is the default
PLC_PORT = 502  # The port PLC communication is taking place

# Function to discover PLCs on the network (if PLC_IP is None)
def discover_plc():
    """
    Attempts to discover a PLC on the network.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Implement PLC discovery logic using the PLC library
        # Example:  (Adapt to your library)
        discovered_plcs = plc_lib.discover_plcs() # Example method from a library
        if discovered_plcs:
            print("Discovered PLCs:")
            for plc in discovered_plcs:
                print(f"  - IP: {plc['ip']}, Name: {plc['name']}")
            # In this simple example, we just take the first PLC found.
            # In a real-world scenario, you'd need more robust logic to identify the target PLC.
            return discovered_plcs[0]['ip']  # Return the IP of the first PLC
        else:
            print("No PLCs discovered on the network.")
            return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None



def collect_io_image(plc_ip, plc_port):
    """
    Collects the I/O Image state of a PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        plc_port (int): The Port of the PLC.
    """
    try:
        # Connect to the PLC
        plc = plc_lib.PLC(plc_ip, plc_port)  # Initialize the PLC object
        plc.connect()

        # Read the Input Image Table
        input_image = plc.read_input_image()
        print("Input Image Table:")
        print(input_image)

        # Read the Output Image Table
        output_image = plc.read_output_image()
        print("\nOutput Image Table:")
        print(output_image)

        # You can further process and store the collected I/O image data here.
        # For example, save it to a file:
        with open("io_image_data.txt", "w") as f:
            f.write("Input Image:\n")
            f.write(str(input_image))
            f.write("\n\nOutput Image:\n")
            f.write(str(output_image))
        print("\nI/O Image data saved to io_image_data.txt")


        # Disconnect from the PLC
        plc.disconnect()

    except plc_lib.PLCConnectionError as e:
        print(f"Error connecting to PLC: {e}")
    except plc_lib.PLCReadError as e:
        print(f"Error reading I/O Image: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    # Determine PLC IP address
    if PLC_IP is None:
        print("PLC IP address not specified. Attempting to discover PLC...")
        PLC_IP = discover_plc()
        if PLC_IP is None:
            print("Could not automatically discover PLC.  Please specify the PLC_IP in the script.")
            exit(1)
        else:
            print(f"PLC discovered at IP address: {PLC_IP}")

    # Collect the I/O Image data
    collect_io_image(PLC_IP, PLC_PORT)