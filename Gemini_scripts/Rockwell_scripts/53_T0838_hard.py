import pycomm3
import time
import socket

# Configuration
PLC_MODEL = "Micro850"  # Update if needed
ALARM_VARIABLE = "_IO_EM_DO_06"  # The tag controlling the Red LED (simulating alarm)
SUPPRESSION_VALUE = False  # Value to suppress the alarm (Red LED off)
RESTORE_DELAY = 60  # Time in seconds to suppress the alarm (optional, for timed suppression)

def find_plc_ip():
    """
    Finds the PLC's IP address on the network.
    This assumes the PLC responds to standard Ethernet/IP discovery.
    """
    # This is a simplified example and may need adjustment based on your network.
    # It uses a broadcast ping to find the PLC.

    # Create a socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Broadcast address (adjust if needed for your network)
    broadcast_address = '255.255.255.255'
    port = 44818  # Standard Ethernet/IP port

    # Message to send (this might need to be a specific discovery message)
    message = b'\x63\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00' # Example CIP Identity Request
    
    # Send the broadcast message
    sock.sendto(message, (broadcast_address, port))

    # Listen for responses (adjust timeout as needed)
    sock.settimeout(5)  # Wait for 5 seconds
    try:
        data, addr = sock.recvfrom(1024)
        print(f"Received response from: {addr[0]}") # Debugging
        plc_ip = addr[0]
        sock.close()
        return plc_ip
    except socket.timeout:
        print("No PLC found on the network.")
        sock.close()
        return None
    except Exception as e:
        print(f"Error during discovery: {e}")
        sock.close()
        return None


def suppress_alarm(plc_ip, alarm_variable, suppression_value):
    """
    Suppresses the specified alarm by writing a new value to its associated tag.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            plc.write(alarm_variable, suppression_value)
            print(f"Alarm {alarm_variable} suppressed (set to {suppression_value}).")
            return True

    except Exception as e:
        print(f"Error suppressing alarm: {e}")
        return False


def restore_alarm(plc_ip, alarm_variable, original_value):
    """
    Restores the alarm to its original value.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            plc.write(alarm_variable, original_value)
            print(f"Alarm {alarm_variable} restored (set back to {original_value}).")
            return True

    except Exception as e:
        print(f"Error restoring alarm: {e}")
        return False

def get_current_alarm_state(plc_ip, alarm_variable):
    """
    Reads the current state of the alarm tag from the PLC.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            response = plc.read(alarm_variable)
            if response.status == 'ok':
                return response.value
            else:
                print(f"Error reading {alarm_variable}: {response.status}")
                return None
    except Exception as e:
        print(f"Error reading alarm state: {e}")
        return None


def main():
    """
    Main function to execute the alarm suppression and restoration.
    """
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("PLC IP address not found. Exiting.")
        return

    # Get the current state of the alarm before suppressing it
    original_alarm_state = get_current_alarm_state(plc_ip, ALARM_VARIABLE)

    if original_alarm_state is None:
        print("Failed to get current alarm state.  Exiting.")
        return

    # Suppress the alarm
    if suppress_alarm(plc_ip, ALARM_VARIABLE, SUPPRESSION_VALUE):
        if RESTORE_DELAY > 0:
            print(f"Alarm will be restored after {RESTORE_DELAY} seconds...")
            time.sleep(RESTORE_DELAY)

            # Restore the alarm to its original value
            restore_alarm(plc_ip, ALARM_VARIABLE, original_alarm_state)
        else:
            print("Alarm suppressed indefinitely.  Manual restoration required.")


if __name__ == "__main__":
    main()