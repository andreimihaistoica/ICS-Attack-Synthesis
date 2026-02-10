import snap7
from snap7.util import get_bool, get_int, get_real, get_dword
from snap7.client import Client
import socket

# Function to find the PLC's IP on the network
def find_plc_ip(port=102, timeout=4):
    message = (
        b'\x03\x00\x00\x16\x11\xe0\x00\x00\x00\x01\x00\xc1\x02\x01\x00\xc2\x02\x01\x00'
        b'\xc0\x01\x09'
    )
    for ip in range(1, 255):  # Adjust range based on your subnet
        ip_address = f"192.168.0.{ip}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((ip_address, port))
                sock.sendall(message)
                response = sock.recv(1024)
                if response:
                    return ip_address
        except Exception:
            pass
    return None


# Function to read data from the PLC
def read_io_image(plc):
    """
    Reads input and output image data from the PLC.
    """
    # Reading input area (I memory)
    input_area = plc.read_area(snap7.types.Areas.PE, 0, 0, 256)  # Adjust size as needed
    # Reading output area (Q memory)
    output_area = plc.read_area(snap7.types.Areas.PA, 0, 0, 256)  # Adjust size as needed

    print(">>> Input Image Table (first 256 bytes):")
    print(input_area)

    print("\n>>> Output Image Table (first 256 bytes):")
    print(output_area)

    # Parse a few example bits/values for demonstration
    input_bit = get_bool(input_area, 0, 0)  # Get first bit of the input image
    output_bit = get_bool(output_area, 0, 0)  # Get first bit of the output image
    first_input_integer = get_int(input_area, 0)  # Get first 16-bit integer in inputs
    first_output_integer = get_int(output_area, 0)  # Get first 16-bit integer in outputs

    print("\nParsed values:")
    print(f"Input Bit 0.0: {input_bit}")
    print(f"Output Bit 0.0: {output_bit}")
    print(f"First Input Integer: {first_input_integer}")
    print(f"First Output Integer: {first_output_integer}")


# Main logic
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
    else:
        print("No PLC found on the network.")
        exit()

    plc = Client()
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200 series
        if plc.get_connected():
            print("Connected to PLC. Reading I/O image table...")
            read_io_image(plc)
        else:
            print("Failed to connect to the PLC.")
    except Exception as e:
        print("Error: ", str(e))
    finally:
        if plc.get_connected():
            plc.disconnect()