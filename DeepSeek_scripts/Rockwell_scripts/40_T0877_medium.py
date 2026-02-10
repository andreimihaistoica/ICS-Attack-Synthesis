from pycomm3 import LogixDriver
import socket

def find_plc_ip(plc_name="Micro850"):
    # This function attempts to find the PLC's IP address by resolving its hostname
    try:
        plc_ip = socket.gethostbyname(plc_name)
        print(f"PLC IP Address found: {plc_ip}")
        return plc_ip
    except socket.error as e:
        print(f"Failed to resolve PLC IP: {e}")
        return None

def collect_io_image(plc_ip):
    try:
        # Connect to the PLC using its IP address
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")

            # Read the input image table
            input_image = plc.read('InputImage')
            print("Input Image Table:")
            print(input_image)

            # Read the output image table
            output_image = plc.read('OutputImage')
            print("Output Image Table:")
            print(output_image)

            # Return the collected I/O Image data
            return {'input_image': input_image, 'output_image': output_image}

    except Exception as e:
        print(f"An error occurred while collecting I/O Image: {e}")
        return None

if __name__ == "__main__":
    # If the PLC IP is not known, find it first
    plc_ip = find_plc_ip()

    if plc_ip:
        # Collect the I/O Image from the PLC
        io_image_data = collect_io_image(plc_ip)

        if io_image_data:
            print("I/O Image collection successful.")
            # Further processing or saving of the data can be done here
        else:
            print("Failed to collect I/O Image.")
    else:
        print("PLC IP address could not be determined.")