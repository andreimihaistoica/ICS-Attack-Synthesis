# requires libraries: pycomm3 (or a similar library for your specific PLC)
#                   scapy (for network discovery, if needed)

import sys
import time
from pycomm3 import CIPDriver, Services, ClassCode, CommonService
from scapy.all import ARP, Ether, srp

# Configuration - adjust as needed
PLC_VENDOR_ID = 0x01 # Rockwell Automation (Allen-Bradley) Vendor ID.  Change for other vendors.
IO_IMAGE_FILE_NAME = "io_image_dump.txt"
DELAY_BETWEEN_READS = 1  # seconds


def discover_plc_ip(network_interface="eth0"):
    """
    Attempts to discover the PLC's IP address on the local network.

    Args:
        network_interface (str): The network interface to use for ARP requests.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    print("Discovering PLC IP address...")
    try:
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.1/24") # Change to your network
        answered_list = srp(arp_request, timeout=3, iface=network_interface, verbose=False)[0] # timeout in secconds
        
        #Iterate to get IPs of Rockwell Automation
        for sent, received in answered_list:
            #Look for Rockwell Automation Vendor ID (0x01) in the ARP response.
            #ARP responses do not carry Vendor ID, so we use the MAC address prefix
            if received.hwsrc.startswith("00:0a:eb") or received.hwsrc.startswith("00:19:b9") or received.hwsrc.startswith("00:04:23"): # RockWell Mac Address prefixes
                print(f"Found PLC with MAC: {received.hwsrc} and IP: {received.psrc}")
                return received.psrc

        print("No Rockwell Automation PLC found on the network.")
        return None

    except Exception as e:
        print(f"Error during network discovery: {e}")
        return None


def read_io_image(plc_ip):
    """
    Reads the I/O Image of a PLC using its Native API (CIP).

    Args:
        plc_ip (str): The IP address of the PLC.

    Returns:
        dict: A dictionary containing the I/O Image data, or None on error.
    """

    try:
        with CIPDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")

            # Request PLC Identification - optional, but useful
            identity = plc.generic_message(
                service=Services.Get_Attribute_All,
                class_code=ClassCode.Identity,
                instance=1,
                unconnected_send=True,
                route_path=True
            )

            if identity.status == 0:
                print(f"PLC Vendor: {identity.value['vendor']}, Product Name: {identity.value['product_name']}, Device Type: {identity.value['device_type']}")
            else:
                print(f"Error getting PLC Identity: {identity.error}")


            # **IMPORTANT:  The following code needs to be adapted to YOUR PLC's specific memory map and data structures.**
            # This is a *generic* example and will NOT work without modification.
            # You will need to consult your PLC's documentation to determine:
            # 1. The Class ID and Instance ID for the I/O Image.
            # 2. The structure of the I/O Image data.
            # 3. How to access the I/O Image data using CIP.

            # **Example (highly simplified - adapt to your PLC):**
            # Assuming I/O Image data is accessible as Class 0x64, Instance 1, Attribute 3.  This is just an example!
            #io_image_data = plc.generic_message(
            #    service=Services.Get_Attribute_Single,
            #    class_code=0x64,  # Example Class ID - CHANGE THIS
            #    instance=1,     # Example Instance ID - CHANGE THIS
            #    attribute=3,    # Example Attribute ID - CHANGE THIS
            #    unconnected_send=True,
            #    route_path=True
            #)

            # **Alternative Example (using a pre-defined tag):**
            #  If you have a named tag in your PLC that holds the I/O image (e.g., "IO_Image")
            #  Uncomment these lines and adjust the tag name.  This is often the easier approach.
            #response = plc.read("IO_Image")  # Replace "IO_Image" with the actual tag name in your PLC
            #if response.status == 0:
            #    io_image_data = response.value
            #else:
            #    print(f"Error reading IO_Image tag: {response.error}")
            #    return None


            # *** Replace the following with your actual I/O Image retrieval code based on your PLC! ***
            # This is a placeholder - it will not work as-is.
            io_image_data = {"Input_1": False, "Output_1": True, "Input_2": True, "Output_2": False}  #Example Data!


            if io_image_data is not None:
                print("Successfully read I/O Image (example data)")
                return io_image_data
            else:
                print("Failed to read I/O Image (see errors above)")
                return None

    except Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None



def save_io_image(io_image_data, filename=IO_IMAGE_FILE_NAME):
    """
    Saves the I/O Image data to a file.

    Args:
        io_image_data (dict): The I/O Image data to save.
        filename (str): The name of the file to save the data to.
    """
    try:
        with open(filename, "w") as f:
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for key, value in io_image_data.items():
                f.write(f"{key}: {value}\n")
        print(f"I/O Image saved to {filename}")
    except Exception as e:
        print(f"Error saving I/O Image to file: {e}")


def main():
    if len(sys.argv) > 1:
        plc_ip = sys.argv[1]  # PLC IP address provided as a command-line argument
    else:
        plc_ip = discover_plc_ip() # Attempt to discover the PLC
        if not plc_ip:
            print("PLC IP address not provided and auto-discovery failed.")
            print("Please provide the PLC IP address as a command-line argument.")
            sys.exit(1)

    print(f"Using PLC IP address: {plc_ip}")

    try:
        while True:
            io_image = read_io_image(plc_ip)
            if io_image:
                save_io_image(io_image)
            else:
                print("Failed to read I/O Image.  Stopping.")
                break

            time.sleep(DELAY_BETWEEN_READS)

    except KeyboardInterrupt:
        print("\nScript interrupted. Exiting.")


if __name__ == "__main__":
    main()