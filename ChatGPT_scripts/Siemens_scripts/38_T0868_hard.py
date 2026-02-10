from scapy.all import ARP, Ether, srp
from pycomm3 import S7Comm
import socket

def find_plc_ip():
    """Scans the network to identify a Siemens PLC based on its MAC or response"""
    target_network = "192.168.1.1/24"  # Adjust network range for your setup
    arp_request = ARP(pdst=target_network)
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether_frame / arp_request
    result = srp(packet, timeout=3, verbose=False)[0]

    for sent, received in result:
        vendor_ip = received.psrc
        mac_address = received.hwsrc.upper()

        # Siemens MAC addresses often begin with these prefixes:  
        siemens_prefixes = ["00:0E:8C", "00:1A:64", "00:1B:1B"]
        if any(mac_address.startswith(prefix) for prefix in siemens_prefixes):
            print(f"Potential Siemens PLC found at: {vendor_ip} with MAC: {mac_address}")
            return vendor_ip

    print("Siemens PLC not detected.")
    return None

def detect_plc_mode(plc_ip):
    """Connects to the Siemens PLC and detects the operating mode"""
    try:
        with S7Comm(plc_ip, rack=0, slot=1) as plc:
            # Query the PLC's mode using the SZL_ID 0x074, Sublist 0x0001
            response = plc.read_szl(0x074, 0x0001)
            if response:
                mode_code = response[0][0]
                plc_modes = {
                    0x00: "RUN", 
                    0x01: "STOP", 
                    0x02: "RUN-P", 
                    0x03: "HALT", 
                    0x04: "STARTUP",
                    0x05: "OTHER"
                }
                mode = plc_modes.get(mode_code, "UNKNOWN")
                print(f"Detected PLC Operating Mode: {mode}")
                return mode
            else:
                print("Failed to retrieve PLC mode.")
                return None
    except Exception as e:
        print(f"Error communicating with PLC: {e}")
        return None

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        detect_plc_mode(plc_ip)