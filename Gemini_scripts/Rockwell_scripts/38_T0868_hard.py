import pycomm3
import time
import socket

def get_plc_ip_address():
    """
    Attempts to automatically discover the PLC's IP address on the network.
    This is a basic example and might need adjustments based on your network configuration.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # Timeout after 5 seconds

        # Broadcast a message to the network (adjust the broadcast address if needed)
        broadcast_address = '255.255.255.255'
        port = 2222  #  Commonly used port for PLC discovery; may need adjustment

        message = b'CIP Discovery Request'  # Or a vendor-specific discovery message

        sock.sendto(message, (broadcast_address, port))

        # Listen for a response
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"PLC IP address discovered: {plc_ip}")
        return plc_ip

    except socket.timeout:
        print("PLC IP address discovery timed out. Please provide the IP address manually.")
        return None
    except Exception as e:
        print(f"Error discovering PLC IP address: {e}")
        return None
    finally:
        sock.close()

def detect_operating_mode(plc_ip):
    """
    Detects the operating mode of a Rockwell Micro850 PLC.
    This script reads the value of specific variables that reflect the state of the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.

    Returns:
        str: The detected operating mode, or None if the mode cannot be determined.
    """

    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Define tags that reflect the PLC state.  Adjust these tags based on the PLC's program.
            # These are *examples*. You *MUST* adjust these based on YOUR PLC's program.
            # A well-designed PLC program will have readily accessible status variables.
            tags_to_read = ['_IO_EM_DO_02', '_IO_EM_DO_06', '_IO_EM_DO_07', 'START', 'STOP']

            # Read the tags
            read_results = plc.read(*tags_to_read)

            # Check for errors
            for result in read_results:
                if result.status != 'Success':
                    print(f"Error reading tag {result.tag}: {result.status}")
                    return None  # Unable to determine operating mode if tags cannot be read.

            # Extract the values
            fan_output = read_results[0].value
            red_led = read_results[1].value
            green_led = read_results[2].value
            start_button = read_results[3].value
            stop_button = read_results[4].value

            # Attempt to determine the operating mode based on the tag values.
            # This logic is HIGHLY dependent on the PLC program's design.
            # This is just an example; adjust it according to how your PLC's program indicates the mode.
            if not fan_output and red_led and not green_led:
                return "Stop Mode (Likely - Based on Red LED)"
            elif fan_output and green_led and not red_led:
                return "Run Mode (Likely - Based on Fan and Green LED)"
            elif start_button and not stop_button:
                return "Ready/Idle Mode (Likely - Based on Start/Stop)"  # May not be a true operating mode

            else:
                return "Unknown Mode"  # Unable to determine based on available information


    except Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None



if __name__ == "__main__":
    # 1. Attempt to automatically discover the PLC's IP address.
    plc_ip = get_plc_ip_address()

    # 2. If discovery fails, prompt the user for the IP address.
    if plc_ip is None:
        plc_ip = input("Enter the PLC's IP address: ")
        if not plc_ip:
            print("No IP address provided.  Exiting.")
            exit()


    # 3. Detect the operating mode.
    operating_mode = detect_operating_mode(plc_ip)

    # 4. Print the result.
    if operating_mode:
        print(f"Detected PLC Operating Mode: {operating_mode}")
    else:
        print("Could not determine PLC operating mode.")