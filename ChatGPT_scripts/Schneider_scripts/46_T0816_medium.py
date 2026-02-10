from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import time

# Network Configuration (Adjust according to your subnet)
SUBNET = "192.168.1.0/24"  # Change according to your network

# Function to find PLC IP
def find_plc_ip():
    print("[*] Scanning the network to identify the PLC IP...")
    
    # ARP Scan to find active devices
    arp_request = ARP(pdst=SUBNET)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for sent, received in answered:
        # Schneider Electric MAC Address Range (Change accordingly if needed)
        if received.hwsrc.startswith("00:80:F4"):  # Common MAC prefix for Schneider Electric devices
            print(f"[+] Found Schneider Electric PLC at {received.psrc}")
            return received.psrc
    
    print("[-] No Schneider Electric PLC found on the network.")
    return None

# Function to send Modbus command to restart the PLC
def restart_plc(ip):
    try:
        print(f"[*] Connecting to PLC at {ip}...")
        client = ModbusTcpClient(ip)
        client.connect()

        # Writing to a control register to trigger a restart
        # Adjust the register address based on PLC documentation (This is an example)
        RESTART_REGISTER = 0x0000  
        RESTART_COMMAND = 0x01  

        print("[*] Sending restart command to PLC...")
        client.write_coil(RESTART_REGISTER, RESTART_COMMAND)

        print("[+] Restart command sent successfully!")
        client.close()

    except Exception as e:
        print(f"[-] Failed to restart PLC: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        restart_plc(plc_ip)
    else:
        print("[-] PLC Restart operation aborted due to missing IP.")