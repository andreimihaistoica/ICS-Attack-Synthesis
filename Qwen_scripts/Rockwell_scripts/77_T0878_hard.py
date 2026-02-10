import pycomm3
from pycomm3 import LogixDriver
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # This is a simple example using a broadcast to find the PLC.
    # In a real-world scenario, you might use a more sophisticated method.
    broadcast_ip = '255.255.255.255'
    port = 44818  # Ethernet/IP port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b'WhoIsThere', (broadcast_ip, port))

    sock.settimeout(5)  # Wait for 5 seconds for a response
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None

# Function to suppress alarms
def suppress_alarms(plc_ip):
    with LogixDriver(plc_ip) as plc:
        # Suppress the alarm by setting the relevant tags to False
        plc.write(('Activate_FanA', False))
        plc.write(('FanA_Off', False))
        plc.write(('Tog_Off', True))  # Prevent the fan from being activated

        # Optionally, you can also reset the timers
        plc.write(('TON_1.IN', False))
        plc.write(('TONOFF_1.IN', False))

        print("Alarms suppressed successfully")

# Main function
def main():
    plc_ip = '192.168.1.10'  # Replace with the actual PLC IP address
    if plc_ip is None:
        plc_ip = discover_plc_ip()
        if plc_ip is None:
            print("Failed to discover PLC IP address")
            return

    suppress_alarms(plc_ip)

if __name__ == "__main__":
    main()