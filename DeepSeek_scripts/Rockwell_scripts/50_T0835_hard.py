from pycomm3 import LogixDriver
import socket

def find_plc_ip():
    # Example: Scan for the PLC's IP address on the network
    # Replace '192.168.1.1/24' with your network range
    # This is a placeholder; you may need to implement a more robust IP discovery method
    target_ip = '192.168.1.100'  # Replace with your PLC's IP address
    return target_ip

def manipulate_io_image(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")

            # Override the I/O image
            # Example: Force _IO_EM_DO_02 (Fan output) to TRUE
            plc.write('_IO_EM_DO_02', True)
            print("Forced _IO_EM_DO_02 (Fan output) to TRUE")

            # Example: Force _IO_EM_DO_07 (Green LED) to FALSE
            plc.write('_IO_EM_DO_07', False)
            print("Forced _IO_EM_DO_07 (Green LED) to FALSE")

            # Example: Force _IO_EM_DO_06 (Red LED) to TRUE
            plc.write('_IO_EM_DO_06', True)
            print("Forced _IO_EM_DO_06 (Red LED) to TRUE")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")

        # Step 2: Manipulate the I/O image
        manipulate_io_image(plc_ip)
    else:
        print("Could not find the PLC on the network.")