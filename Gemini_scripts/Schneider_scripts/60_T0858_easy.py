import socket
import struct
import time

# Configuration - Modify these based on your PLC and network setup
PLC_IP = None  # Initially unknown, will be discovered
PLC_PORT = 502  # Standard Modbus port (adjust if needed)
TARGET_MODE = "program"  # Desired mode: "program", "run", "stop" (case-insensitive)
DISCOVERY_IP_RANGE = "192.168.1."  # IP range for PLC discovery
DISCOVERY_TIMEOUT = 2  # Seconds to wait for a response during discovery

# Vendor-specific code and mode change mechanism.  **CRITICAL:  Replace these!**
#  This is placeholder code.  You MUST replace these with code that
#  correctly interacts with *your* specific PLC vendor and model.
#
# The example below provides a Modbus register write example.  However,
# most PLCs will NOT use a simple Modbus write for mode changes due to
# security and operational concerns.
#
# Consult your PLC's documentation for the *correct* method to change
# the operating mode.  This might involve:
#
# *  A specific Modbus function code (not just write register).
# *  A proprietary protocol over TCP/IP or UDP.
# *  A command sent via a serial connection.
# *  Authentication/authorization steps before the mode change.
#

# Placeholder Modbus register address and value for setting the PLC mode.
# *REPLACE THESE WITH THE CORRECT VALUES FOR YOUR PLC!*
MODE_CHANGE_REGISTER = 40001
MODE_PROGRAM_VALUE = 1
MODE_RUN_VALUE = 2
MODE_STOP_VALUE = 3

def discover_plc_ip(ip_range):
    """
    Scans a network range to discover the PLC's IP address by sending ICMP Echo Requests (ping).
    This relies on ICMP being enabled, which is often disabled in ICS environments for security.

    Args:
        ip_range: The base IP range (e.g., "192.168.1.").  The last octet will be scanned.

    Returns:
        The PLC's IP address as a string, or None if not found.
    """

    print("Attempting to discover PLC IP address...")
    for i in range(1, 255):  # Iterate through the last octet
        ip_address = ip_range + str(i)
        try:
            socket.inet_aton(ip_address)  # Check if valid IP

            # Create a raw socket to send ICMP packets. Requires root privileges on many systems.
            icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            icmp_socket.settimeout(DISCOVERY_TIMEOUT) # Set a timeout to avoid indefinite blocking
            icmp_socket.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)  # Tell the kernel we will provide the IP header
            icmp_socket.bind(('', 0))

            packet = create_icmp_packet()

            start_time = time.time()
            icmp_socket.sendto(packet, (ip_address, 1))

            try:
                data, addr = icmp_socket.recvfrom(1024) #receive the ping reply
                end_time = time.time()
                rtt = (end_time - start_time) * 1000

                print(f"Ping reply from {addr[0]}  time={rtt:.2f} ms")

                icmp_socket.close()
                print(f"PLC IP address found: {ip_address}")
                return ip_address
            except socket.timeout:
                icmp_socket.close()
                pass #timeout, not found, we continue to the next IP address.
        except socket.error as e:
            print(f"Error pinging {ip_address}: {e}")

    print("PLC IP address not found in the specified range.")
    return None

def create_icmp_packet():
    """
    Creates a simple ICMP echo request packet.

    Returns:
        The ICMP packet as bytes.
    """
    # ICMP Header
    icmp_type = 8  # Echo request
    icmp_code = 0
    icmp_checksum = 0
    icmp_id = 12345  # Identifier
    icmp_sequence = 1

    # Combine header fields
    header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_sequence)

    # Calculate checksum (simple checksum)
    packet = header + b"ExampleICMPPayload"  # Add some data. can be empty.
    icmp_checksum = calculate_checksum(packet)

    # Re-pack header with correct checksum
    header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_sequence)

    return header + b"ExampleICMPPayload"

def calculate_checksum(data):
    """
    Calculates the ICMP checksum.

    Args:
        data: The ICMP packet data as bytes.

    Returns:
        The calculated checksum.
    """
    s = 0
    n = len(data) % 2
    for i in range(0, len(data)-n, 2):
        s += data[i] + (data[i+1] << 8)
    if n:
        s += data[len(data)-1]
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xffff
    return s

def change_plc_mode(plc_ip, plc_port, target_mode):
    """
    Changes the operating mode of the PLC.  **IMPORTANT: Replace the Modbus code
    with the *correct* code for your PLC.**

    Args:
        plc_ip: The IP address of the PLC.
        plc_port: The port number the PLC is listening on (usually 502 for Modbus).
        target_mode: The desired mode ("program", "run", "stop").

    Returns:
        True if the mode change was successful (according to the Modbus write), False otherwise.
    """

    try:
        # Determine the mode value based on the target mode string
        if target_mode.lower() == "program":
            mode_value = MODE_PROGRAM_VALUE
        elif target_mode.lower() == "run":
            mode_value = MODE_RUN_VALUE
        elif target_mode.lower() == "stop":
            mode_value = MODE_STOP_VALUE
        else:
            print(f"Invalid target mode: {target_mode}")
            return False

        # Create a Modbus TCP client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)  # Set a timeout
        client_socket.connect((plc_ip, plc_port))

        # Craft a Modbus write single register request.  This is a placeholder!
        # Transaction Identifier (2 bytes), Protocol Identifier (2 bytes), Length (2 bytes), Unit Identifier (1 byte)
        transaction_id = 1  # Example transaction ID
        protocol_id = 0
        length = 6  # Length of the remaining bytes (including function code, etc.)
        unit_id = 1  # Slave address (often 1, but check your PLC's configuration)

        # Modbus PDU (Protocol Data Unit)
        function_code = 6  # Write Single Register (Modbus function code)
        register_address = MODE_CHANGE_REGISTER - 1  # Modbus registers are 1-based, not 0-based
        register_value = mode_value  # The desired mode value.

        # Pack the Modbus ADU (Application Data Unit)
        message = struct.pack(">HHHBBHH", transaction_id, protocol_id, length, unit_id, function_code, register_address, register_value)

        # Send the Modbus request
        client_socket.sendall(message)

        # Receive the response
        response = client_socket.recv(1024)  # Adjust buffer size as needed.
        client_socket.close()

        # Basic response validation (replace with more thorough validation)
        if len(response) < 8:
            print("Invalid Modbus response: Too short.")
            return False

        # Unpack the response
        response_transaction_id, response_protocol_id, response_length, response_unit_id, response_function_code, response_register_address, response_register_value = struct.unpack(">HHHBBHH", response[:12])

        # Check for errors in the response
        if function_code + 0x80 == response_function_code:
            #This is a Modbus Exception response.
            exception_code = struct.unpack(">B", response[8:9])[0] # extract the exception code.
            print(f"Modbus Error. The response from the PLC indicated an error: {exception_code}")
            return False

        # Check if the transaction ID matches
        if transaction_id != response_transaction_id:
            print("Transaction ID mismatch in response.")
            return False

        # Check if the function code matches
        if function_code != response_function_code:
            print("Function code mismatch in response.")
            return False


        print(f"Successfully set PLC mode to {target_mode}.")
        return True

    except socket.timeout:
        print("Socket timeout.  PLC may be unreachable or not responding.")
        return False
    except ConnectionRefusedError:
        print("Connection refused.  PLC may not be listening on the specified port.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    # Discover the PLC's IP address if not already known
    if PLC_IP is None:
        PLC_IP = discover_plc_ip(DISCOVERY_IP_RANGE)
        if PLC_IP is None:
            print("Failed to discover PLC IP.  Exiting.")
            exit(1)

    # Change the PLC's operating mode
    if change_plc_mode(PLC_IP, PLC_PORT, TARGET_MODE):
        print("PLC mode change completed successfully.")
    else:
        print("PLC mode change failed.")