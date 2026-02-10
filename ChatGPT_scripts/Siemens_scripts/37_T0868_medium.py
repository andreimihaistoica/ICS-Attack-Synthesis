from scapy.all import Ether, ARP, srp
import snap7
import struct

def find_plc_ip(network="192.168.0.1/24"):
    print("[+] Scanning for Siemens S7-1200 PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network), timeout=2, verbose=False)

    for sent, received in ans:
        if is_siemens_plc(received.psrc):  # Check if it's an S7 device
            print(f"[!] Siemens S7-1200 PLC found: {received.psrc}")
            return received.psrc
    print("[-] No Siemens PLC detected in the network.")
    return None

def is_siemens_plc(ip):
    try:
        client = snap7.client.Client()
        client.connect(ip, 0, 1, 102)  # Rack=0, Slot=1
        client.disconnect()
        return True
    except:
        return False

def get_plc_mode(plc_ip):
    try:
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1, 102)  # Connect to the PLC

        mode = client.get_cpu_state()
        client.disconnect()

        mode_str = {
            snap7.types.cpu_status_run: "RUN",
            snap7.types.cpu_status_stop: "STOP",
            snap7.types.cpu_status_unknown: "UNKNOWN"
        }.get(mode, "UNKNOWN")

        print(f"[+] PLC Operating Mode: {mode_str}")

    except Exception as e:
        print(f"[-] Error retrieving PLC mode: {e}")

# Run the script
plc_ip = find_plc_ip("192.168.0.1/24")  # Modify network range if needed
if plc_ip:
    get_plc_mode(plc_ip)