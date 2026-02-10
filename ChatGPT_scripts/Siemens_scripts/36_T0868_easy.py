from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import socket

# Network details (Modify based on your subnet)
SUBNET = "192.168.1.0/24"

# Function to scan for the PLC based on an open Modbus TCP Port (default: 502)
def find_plc_ip():
    print("[*] Scanning network to find PLC...")
    arp = ARP(pdst=SUBNET)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    
    result = srp(ether/arp, timeout=3, verbose=0)[0]
    
    for sent, received in result:
        ip = received.psrc
        try:
            # Check if Modbus port (502) is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((ip, 502)) == 0:
                print(f"[*] PLC detected at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            pass
    return None

# Function to read PLC operating mode
def detect_plc_mode(plc_ip):
    try:
        client = ModbusTcpClient(plc_ip, port=502)
        client.connect()
        print("[*] Connected to PLC.")

        # Vendor-specific Modbus register (modify based on the PLC model)
        MODE_REGISTER = 0x1000  # Example register (depends on vendor documentation)

        response = client.read_holding_registers(MODE_REGISTER, 1)
        if response.isError():
            print("[!] Error reading PLC mode.")
            return
        
        mode_value = response.registers[0]
        
        modes = {
            0: "Program Mode",
            1: "Run Mode",
            2: "Remote Mode",
            3: "Stop Mode",
            4: "Reset Mode",
            5: "Test/Monitor Mode"
        }

        mode_name = modes.get(mode_value, "Unknown Mode")
        print(f"[*] PLC Operating Mode: {mode_name}")

        client.close()
    except Exception as e:
        print(f"[!] Error communicating with PLC: {e}")

# Main execution
plc_ip = find_plc_ip()
if plc_ip:
    detect_plc_mode(plc_ip)
else:
    print("[!] No PLC found on the network.")