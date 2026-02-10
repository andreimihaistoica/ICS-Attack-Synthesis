import snap7
import struct
import socket
import subprocess

# Function to get the PLC's IP address (if not known)
def get_plc_ip_address():
    """
    Attempts to discover the PLC's IP address by pinging a range of potential addresses
    and checking for a response on the S7 port (102).  This is a basic approach
    and might need adjustments based on network configuration.

    Returns:
        str: The PLC's IP address if found, None otherwise.
    """
    # You can adjust the IP range as needed.  Make it relevant to your network.
    network_prefix = "192.168.1."  # Example:  Change to your actual network prefix
    for i in range(1, 255): #Check all possible ips
        ip_address = network_prefix + str(i)
        try:
            # Ping the address
            ping_command = ['ping', '-n', '1', ip_address]  # -n 1 for single ping (Windows)
            ping_result = subprocess.run(ping_command, capture_output=True, text=True, timeout=2)

            if ping_result.returncode == 0:  # Ping successful (adjust as needed)
                # Check for S7 port open (102) using socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)  # Short timeout for connection attempt
                try:
                    sock.connect((ip_address, 102))
                    print(f"PLC Found at IP Address: {ip_address}")
                    sock.close()
                    return ip_address
                except socket.error:
                    sock.close()
                    pass  # Port 102 is not open

        except Exception as e:
            print(f"Error during network scan {e}")
            pass #Handles errors such as timeout or command not found

    print("PLC IP address not found in the specified range.")
    return None


def get_plc_mode(plc_ip):
    """
    Retrieves the PLC's operating mode by reading a specific memory location.
    This address and data interpretation is specific to Siemens S7-1200 PLCs and the
    method often relies on vendor specific memory locations.

    Args:
        plc_ip (str): The IP address of the PLC.

    Returns:
        str:  A string representing the PLC's operating mode, or "Unknown" if the mode
              cannot be determined or if there is an error.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 2)  # Rack 0, Slot 2 (typical for S7-1200)

        # Address to read the PLC mode. This is very PLC-specific. You might need to adjust this.
        # This example assumes the mode is stored in Memory Byte 100 (MB100).
        # Consult your PLC's documentation.
        mode_byte = plc.read_area(snap7.const.areas['MK'], 0, 100, 1) #Read one byte from memory byte 100
        plc.disconnect()

        mode_value = mode_byte[0] # Access the byte value

        # Interpret the byte value. This mapping is also PLC-specific.
        if mode_value == 0:
            return "STOP"
        elif mode_value == 1:
            return "RUN"
        elif mode_value == 2:
            return "REMOTE"
        elif mode_value == 3:
            return "PROGRAM"
        elif mode_value == 4:
            return "RESET" #Potentially warm reset
        elif mode_value == 5:
            return "TEST/MONITOR"
        else:
            return "Unknown"

    except Exception as e:
        print(f"Error reading PLC mode: {e}")
        return "Unknown"


if __name__ == "__main__":
    plc_ip_address = get_plc_ip_address() #Attempt to autodiscover the IP

    if plc_ip_address:
        print(f"Found PLC at {plc_ip_address}, attempting to read operating mode.")
    else:
        plc_ip_address = input("Enter the PLC's IP address: ") #Or prompt user

    if plc_ip_address:
        mode = get_plc_mode(plc_ip_address)
        print(f"PLC Operating Mode: {mode}")
    else:
        print("No PLC IP address provided.  Exiting.")