import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the subnet to scan (adjust as needed)
    subnet = "192.168.1."
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

# Function to read I/O Image state
def read_io_image(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Define the tags to read
            tags = [
                'NewVariable',
                'Activate_FanA',
                'FanA_Timer',
                'START',
                'STOP',
                'TON_1.IN',
                'TON_1.PT',
                'TON_1.Q',
                'TON_1.ET',
                'TON_1.Pdate',
                'TON_1.Redge',
                'TONOFF_1.IN',
                'TONOFF_1.PT',
                'TONOFF_1.PTOF',
                'TONOFF_1.Q',
                'TONOFF_1.ET',
                'TONOFF_1.PDATE',
                'TONOFF_1.REDGE',
                'TONOFF_1.FEDGE',
                'FanA_Off',
                'Tog_Off',
                '_IO_EM_DO_02',
                '_IO_EM_DO_06',
                '_IO_EM_DO_07'
            ]
            
            # Read the tags
            results = plc.read(*tags)
            
            # Print the results
            for tag, value in results:
                print(f"{tag}: {value}")
    except Exception as e:
        print(f"Error reading I/O Image: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        read_io_image(plc_ip)

if __name0 == "__main__":
    main()