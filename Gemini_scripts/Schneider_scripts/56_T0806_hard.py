import snap7
import time
import socket
import struct

# Configuration
PLC_IP = None  # Initialize PLC_IP to None, will be discovered if needed
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = None # Data Block Number (Not used in this program)
OUTPUT_BYTE = 0
OUTPUT_BIT = 0 # Q0.0 is the Fan output.  Changing it.

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by broadcasting a discovery message.
    This is a simplified approach and may not work in all network configurations.
    """
    # Define the discovery message (this is Schneider Electric specific; you'll need to find the correct message)
    discovery_message = b"\x00\x01\x00\x00\x00\x00"  # Example;  Adapt to Schneider Electric's Discovery Protocol

    # Create a UDP socket
    sock = socket.socket(socket.socket.AF_INET, socket.socket.SOCK_DGRAM)
    sock.setsockopt(socket.socket.SOL_SOCKET, socket.socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Timeout after 5 seconds

    # Broadcast the discovery message
    sock.sendto(discovery_message, ('<broadcast>', 49152))  # Port 49152 is a common Schneider Electric port. Check your PLC's documentation

    try:
        # Receive the response
        data, addr = sock.recvfrom(1024)
        print(f"Received discovery response from: {addr[0]}")  # Print the IP, but need more data to ensure it's the correct IP address.
        sock.close()
        return addr[0]  # Return the IP address from the response

    except socket.timeout:
        print("PLC IP address discovery timed out.  Check network configuration and discovery message.  Set PLC_IP manually.")
        sock.close()
        return None # Return None if discovery fails

def toggle_output(client, output_byte, output_bit):
    """
    Toggles a specific output bit on the PLC.
    """
    try:
        # Read the current state of the output byte
        byte_array = client.read_area(snap7.constants.S7AreaPA, 0, output_byte, 1)
        current_byte = byte_array[0]

        # Determine if the bit is currently set or not
        bit_mask = 1 << output_bit
        if (current_byte & bit_mask) > 0:
            # Bit is set, clear it
            new_byte = current_byte & (~bit_mask)
            print("Clearing bit")
        else:
            # Bit is clear, set it
            new_byte = current_byte | bit_mask
            print("Setting bit")

        # Write the new byte value back to the PLC
        byte_array[0] = new_byte
        client.write_area(snap7.constants.S7AreaPA, 0, output_byte, byte_array)


    except Exception as e:
        print(f"Error toggling output: {e}")


def main():
    global PLC_IP

    # If PLC_IP is not set, attempt to discover it
    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("PLC IP address discovery failed. Please configure PLC_IP manually.")
            return  # Exit if discovery fails


    # Create a Snap7 client
    client = snap7.client.Client()

    try:
        # Connect to the PLC
        client.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Brute-force I/O: Toggle Q0.0 (Fan output) rapidly
        for i in range(20):  # Toggle it 20 times
            toggle_output(client, OUTPUT_BYTE, OUTPUT_BIT)
            time.sleep(0.5)  # Short delay between toggles


    except Exception as e:
        print(f"Error connecting to PLC: {e}")

    finally:
        # Disconnect from the PLC
        if client.get_connected():
            client.disconnect()
            client.destroy()
            print("Disconnected from PLC")

if __name__ == "__main__":
    main()