import socket
import subprocess
import time
import re  # For IP address extraction

def get_plc_ip_address(engineering_workstation_ip):
    """
    Attempts to discover the PLC's IP address by querying the engineering workstation.
    This is a simplified example and assumes a specific command that might work 
    on the engineering workstation.  This would need to be adapted to match 
    the tools available and communication protocols used on the target network.

    Args:
        engineering_workstation_ip (str): IP address of the engineering workstation.

    Returns:
        str: The PLC's IP address, or None if not found.
    """

    try:
        # Example command (REPLACE WITH A VALID COMMAND for your environment)
        # This is a placeholder.  It's crucial to use a command that actually 
        # returns the PLC's IP address from the engineering workstation.
        command = f"ping {engineering_workstation_ip} -c 1"  # A ping command.  Replace with something more informative.
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            # **IMPORTANT:**  This is a placeholder.  Adapt this regex to 
            # *correctly extract* the PLC IP from the command's output.
            # The format of the output depends *entirely* on the actual command used.
            # Example:  Let's say the `result.stdout` looks like this:
            # "Reply from 10.0.0.100: bytes=32 time<1ms TTL=64"
            # You'd need a regex like:  r"Reply from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

            plc_ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", result.stdout)

            if plc_ip_match:
                return plc_ip_match.group(1)
            else:
                print("PLC IP address not found in command output. Adjust the regex.")
                return None
        else:
            print(f"Error running command: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("Command timed out.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def block_serial_com(plc_ip, com_port):
    """
    Blocks a serial COM port on a serial-to-Ethernet converter by opening and holding a TCP connection.

    Args:
        plc_ip (str): IP address of the PLC (which is connected to the converter).  This assumes the converter's IP is the same.  Adjust if it's different.
        com_port (int): The serial COM port number to block (e.g., 1, 2, 3).
    """

    port = 20000 + com_port  # Calculate the TCP port based on the COM port
    print(f"Attempting to block serial COM port {com_port} (TCP port {port}) on IP: {plc_ip}")

    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        s.connect((plc_ip, port))
        print(f"Successfully connected to {plc_ip}:{port}. Holding connection open...")

        # Hold the connection open indefinitely (or until manually interrupted)
        while True:
            time.sleep(60)  # Keep the connection alive by sleeping.  Adjust time as needed.

    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("Interrupted. Closing the connection.")
    finally:
        if 's' in locals() and s:  # Check if the socket was created
            s.close()
            print("Connection closed.")


if __name__ == "__main__":
    ENGINEERING_WORKSTATION_IP = "192.168.1.100"  # Replace with the actual IP
    COM_PORT_TO_BLOCK = 1  # The COM port you want to block

    plc_ip = get_plc_ip_address(ENGINEERING_WORKSTATION_IP)

    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        block_serial_com(plc_ip, COM_PORT_TO_BLOCK)
    else:
        print("Failed to determine PLC IP address.  Exiting.")