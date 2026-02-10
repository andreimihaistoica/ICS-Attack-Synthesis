import socket
import time
import subprocess
import re

def find_plc_ip_address():
    """
    Attempts to find the PLC's IP address by pinging a known IP range and checking for a specific MAC address.
    This is a rudimentary method and may need adjustment based on the specific network configuration.
    Assumes Siemens PLCs have a MAC address starting with '00-08-DC'.
    """

    #  Adjust the IP range according to your network.  This example assumes a /24 subnet.
    base_ip = "192.168.1." # Change this to match the beginning of your PLC IP.
    plc_mac_prefix = "00-08-DC"  # Siemens PLC MAC prefix

    for i in range(1, 255):  # Iterate through a /24 subnet
        ip_address = base_ip + str(i)
        try:
            # Ping the IP address using subprocess.  Using shell=True is generally discouraged
            # for security reasons but simplifies this specific task.  If security is paramount,
            # use a different ping library (e.g., scapy) and avoid shell=True.  Also, adjust
            # the timeout value to suit your network conditions.
            result = subprocess.run(["ping", "-n", "1", "-w", "100", ip_address], capture_output=True, text=True, timeout=1, check=False) # -n 1 means send 1 echo request, -w 100 set timeout to 100ms
            
            if result.returncode == 0:  # Ping was successful
                #  Check ARP table.  Again, this is system-dependent.
                arp_result = subprocess.run(["arp", "-a", ip_address], capture_output=True, text=True, check=False)
                arp_output = arp_result.stdout.lower()

                if plc_mac_prefix.lower() in arp_output:
                    print(f"Found PLC IP Address: {ip_address}")
                    return ip_address
            
        except subprocess.TimeoutExpired:
            pass  # Ping timed out, move to the next IP
        except Exception as e:
            print(f"Error during ping: {e}")

    print("PLC IP address not found in the specified range.")
    return None



def block_serial_com_port(serial_to_ethernet_converter_ip, com_port):
    """
    Blocks a serial COM port by opening and holding a TCP connection to the
    serial-to-Ethernet converter.

    Args:
        serial_to_ethernet_converter_ip (str): The IP address of the converter.
        com_port (int): The COM port number to block (1, 2, 3, etc.).
    """

    port = 20000 + com_port  # Calculate the TCP port (e.g., COM1 -> 20001)

    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        s.connect((serial_to_ethernet_converter_ip, port))
        print(f"Successfully connected to {serial_to_ethernet_converter_ip}:{port}")

        # Keep the connection open indefinitely (or until manually interrupted)
        print("Holding the connection open. Press Ctrl+C to terminate.")
        while True:
            time.sleep(60)  # Sleep for 60 seconds to avoid excessive CPU usage.
            # You might want to add some simple keep-alive message here if the
            # converter drops idle connections after a while.
            # Example: s.send(b"\n")  # Send a newline character
    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("Connection terminated by user.")
    finally:
        if 's' in locals():  # Ensure socket is defined before closing
            s.close()
            print("Connection closed.")


if __name__ == "__main__":
    # 1. Find the PLC IP Address
    plc_ip = find_plc_ip_address()

    if plc_ip is None:
        print("Could not find PLC IP.  Exiting.")
        exit(1)

    # 2. Hardcoded Serial-to-Ethernet Converter IP (Replace with your actual IP)
    serial_to_ethernet_converter_ip = "10.0.0.1"

    # 3. COM Port to Block
    com_port_to_block = 1  # Block COM1

    # 4. Block the Serial COM Port
    block_serial_com_port(serial_to_ethernet_converter_ip, com_port_to_block)