import socket
import time
import subprocess
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by examining network traffic.
    This is a rudimentary approach and might not be reliable in all network configurations.
    It relies on a simple ping-based discovery.  Adjust the subnet and ping count as needed.
    """
    subnet = "10.0.0" #Adjust to your subnet
    ping_count = 1 #Adjust ping count as necessary

    for i in range(1, 255):  # Iterate through possible IP addresses in the subnet
        ip_address = f"{subnet}.{i}"
        try:
            result = subprocess.run(['ping', '-n', str(ping_count), ip_address], capture_output=True, text=True, timeout=2)
            #print(f"Pinged {ip_address}: {result.returncode}") # for debugging
            if result.returncode == 0:
                # Check for a response indicating a control system device.  This is VERY rudimentary.
                #  A more robust solution would inspect the device's HTTP headers, SNMP responses, etc.
                # This relies on ping response time.  This is unreliable and only for demonstration.
                if "Reply from" in result.stdout:
                    logging.info(f"Potential PLC IP found: {ip_address} (Based on ping response)")
                    return ip_address #return the PLC if it responds to ping

        except subprocess.TimeoutExpired:
            # Ignore timeout errors
            pass
        except Exception as e:
            logging.error(f"Error during IP discovery: {e}")
            return None

    logging.warning("PLC IP address not found using ping sweep.  You may need to manually set the PLC_IP.")
    return None


def block_serial_com(plc_ip, com_port):
    """
    Attempts to block a serial COM port on a serial-to-Ethernet converter by holding open a TCP connection.

    Args:
        plc_ip (str): The IP address of the (serial to ethernet converter connected to the) PLC.  Crucially, this should be the converter IP, not the PLC IP directly (unless they are the same, which is uncommon)
        com_port (int): The COM port number to block (e.g., 1 for COM1).
    """
    converter_port = 20000 + com_port  # Assuming the converter uses ports 20001, 20002, 20003, etc.
    logging.info(f"Attempting to block serial COM port {com_port} by connecting to {plc_ip}:{converter_port}")

    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout for the initial connection attempt

        # Connect to the serial-to-Ethernet converter
        sock.connect((plc_ip, converter_port))
        logging.info(f"Successfully connected to {plc_ip}:{converter_port}")

        # Hold the connection open indefinitely (or until manually interrupted)
        while True:
            time.sleep(60)  # Keep the connection alive.  Adjust as needed.
            # You can optionally send a small keep-alive message here, depending on the converter.
            # sock.send(b"\n") # Example keep-alive (a newline character)
            # sock.recv(1024) # Example receive a keep alive response.  This will block if nothing is sent.
            pass #if no keep alive is needed, just pass.


    except socket.timeout:
        logging.error(f"Connection to {plc_ip}:{converter_port} timed out.")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.  Closing connection.")
    finally:
        if sock:
            sock.close()
            logging.info("Connection closed.")



if __name__ == "__main__":
    PLC_IP = find_plc_ip() # Attempt to find the PLC's IP address
    if not PLC_IP:
         #If not found, manually set the PLC_IP
        PLC_IP = input("Could not automatically determine the PLC IP address. Please enter the IP address of the Serial to Ethernet Converter: ") #Manually set IP
        if not PLC_IP:
            print("PLC IP address required. Exiting.")
            exit()

    COM_PORT_TO_BLOCK = 1  # Change this to the desired COM port number

    block_serial_com(PLC_IP, COM_PORT_TO_BLOCK)