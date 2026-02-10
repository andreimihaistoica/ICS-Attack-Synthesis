import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # Scan the subnet for devices
    for i in range(1, 255):
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
    print("PLC not found in the specified subnet.")
    return None

# Function to read the I/O Image from the PLC
def read_io_image(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Read the input and output image tables
            input_image = plc.read("InputImage")
            output_image = plc.read("OutputImage")
            
            # Print the results
            print("Input Image:")
            print(input_image)
            print("Output Image:")
            print(output_image)
    except Exception as e:
        print(f"Error reading I/O Image: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Read the I/O Image from the PLC
        read_io_image(plc_ip)

if __name__ == "__main__":
    main()