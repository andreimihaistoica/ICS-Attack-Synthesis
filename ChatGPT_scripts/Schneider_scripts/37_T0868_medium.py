import socket
import subprocess
import ipaddress
from pymodbus.client import ModbusTcpClient

def find_plc_ip():
    """ Attempts to find the PLC IP by scanning the local subnet. """
    local_ip = socket.gethostbyname(socket.gethostname())  # Get local machine IP
    subnet = ipaddress.IPv4Network(local_ip + "/24", strict=False)  # Assuming /24 subnet
    
    for ip in subnet.hosts():
        ip_str = str(ip)
        try:
            result = subprocess.run(["ping", "-c", "1", ip_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if "bytes from" in result.stdout:
                return ip_str  # Return first responding device (assuming it's the PLC)
        except Exception as e:
            continue
    return None

def get_plc_mode(ip):
    """ Reads the PLC operating mode using Modbus TCP. """
    client = ModbusTcpClient(ip, port=502)
    
    if not client.connect():
        print("[!] Failed to connect to PLC")
        return None

    # Read PLC system register for operating mode (address 0x78D0 is a common example)
    mode_register = 0x78D0
    response = client.read_input_registers(mode_register, count=1, unit=1)  # Adjust unit ID as needed

    client.close()
    
    if not response.isError():
        mode = response.registers[0]
        return interpret_mode(mode)
    else:
        print("[!] Failed to read PLC mode register")
        return None

def interpret_mode(mode):
    """ Interprets the PLC mode based on known values. """
    mode_mapping = {
        0: "STOP",
        1: "RUN",
        2: "PROGRAM",
        3: "REMOTE",
        4: "TEST/MONITOR",
        5: "RESET"
    }
    return mode_mapping.get(mode, "UNKNOWN")

if __name__ == "__main__":
    print("[*] Searching for PLC on network...")
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"[*] PLC Found at {plc_ip}")
        
        print("[*] Reading PLC Operating Mode...")
        mode = get_plc_mode(plc_ip)
        
        if mode:
            print(f"[+] PLC is currently in {mode} mode.")
        else:
            print("[!] Unable to determine PLC mode.")
    else:
        print("[!] No PLC found on the network.")