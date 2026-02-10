import pycomm3
import socket
import struct

# Configuration - You might need to adjust these based on your specific setup
PLC_IP = None  # Initialize PLC_IP to None.  We will discover it later if needed.
COMMUNICATION_PATH = '1,0' # Adjust if necessary, typically matches your RSLinx setup.

# Function to attempt to discover the PLC's IP address.  Simple broadcast ping.
def discover_plc_ip():
    """Attempts to discover the PLC's IP address by sending a broadcast ping."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)  # Timeout after 5 seconds

        # Craft a simple Ethernet/IP 'List Identity' request.  This is a minimal request.
        request = b'\x63\x00' # Unconnected Send
        request += b'\x04\x00' # Message Length
        request += b'\x02\x00' # Sequence Count
        request += b'\x00\x00' # Service Code (List Identity)
        request += b'\x01\x00\x00\x00' # Priority and Timeout

        s.sendto(request, ('255.255.255.255', 44818))  # CIP Port 44818

        try:
            data, addr = s.recvfrom(1024)
            print(f"Received response from: {addr}")
            return addr[0]  # Return the IP address
        except socket.timeout:
            print("No PLC responded to the broadcast ping.")
            return None  # Could not discover the IP address

    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None
    finally:
        s.close()



def get_micro850_operating_mode(plc_ip):
    """
    Connects to a Rockwell Micro850 PLC and attempts to read the operating mode.
    Uses the _SYS_STATUS tag (common for Micro800 series) to infer the operating mode.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as comm:
            comm.Timeout = 10  # Increase timeout if needed for slow networks
            # Micro800 PLCs use '1,0' for the communication path by default. Double-check in RSLinx.
            # You might need to adapt the path based on your network configuration.
            comm.Path = COMMUNICATION_PATH
            status_tag = '_SYS_STATUS'  # The common status tag.  Check in Connected Components Workbench.

            try:
                read_result = comm.read(status_tag)

                if read_result.status == 'Success':
                    status_word = read_result.value  # Assuming _SYS_STATUS is an INT/DINT

                    # Decode the status word (may require adjustment based on your specific CCW configuration)
                    # The specific bits that indicate operating mode can vary.  Consult Rockwell documentation
                    # or reverse engineer the tag's behavior using Connected Components Workbench.

                    # This is an EXAMPLE decoding.  You MUST adapt this to your PLC.
                    if status_word & 0x0001:
                        operating_mode = "Program"
                    elif status_word & 0x0002:
                        operating_mode = "Run"
                    elif status_word & 0x0004:
                        operating_mode = "Remote"
                    elif status_word & 0x0008:
                        operating_mode = "Stop"
                    elif status_word & 0x0010:
                        operating_mode = "Test/Monitor"
                    else:
                        operating_mode = "Unknown"

                    print(f"PLC Operating Mode: {operating_mode}")
                    return operating_mode

                else:
                    print(f"Error reading {status_tag}: {read_result.status}")
                    return None

            except Exception as e:
                print(f"Error reading status tag: {e}")
                return None

    except Exception as e:
        print(f"Connection Error: {e}")
        return None




if __name__ == "__main__":
    if PLC_IP is None:
        print("PLC IP address not provided. Attempting to discover...")
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("Could not discover PLC IP. Please manually set the PLC_IP variable.")
            exit()
        else:
            print(f"Discovered PLC IP: {PLC_IP}")

    mode = get_micro850_operating_mode(PLC_IP)

    if mode:
        print("Successfully determined operating mode.")
    else:
        print("Failed to determine operating mode.")