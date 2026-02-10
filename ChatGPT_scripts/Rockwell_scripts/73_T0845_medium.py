import socket
import struct
import time
from pycomm3 import CIPDriver

def discover_plc(network_prefix):
    """
    Discover Rockwell PLC in the specified network range.
    :param network_prefix: e.g., '192.168.1.'
    :return: IP address of the discovered PLC
    """
    for i in range(1, 255):  # Scanning through possible hosts in a /24 subnet
        ip = f"{network_prefix}{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                if sock.connect_ex((ip, 44818)) == 0:  # Port 44818 is used by Rockwell PLCs
                    print(f"[+] PLC Found at {ip}")
                    return ip
        except Exception as e:
            pass
    return None

def upload_plc_program(plc_ip):
    """
    Connects to the PLC and attempts to upload the program.
    :param plc_ip: IP address of the PLC
    """
    try:
        with CIPDriver(f"ethernet-ip://{plc_ip}") as plc:
            if plc.open():
                print("[+] Connection Established with PLC")
                
                # CIP Service to Upload Program (hypothetical example)
                response = plc.generic_message(
                    service=0x4C,  # CIP service for Read Tag (example)
                    class_code=0x67,  # Class code for Programming Interface (example)
                    instance=1,
                    request_data=b""
                )

                if response:
                    print("[+] Successfully retrieved the PLC program data.")
                    with open("plc_program_upload.bin", "wb") as f:
                        f.write(response)
                    print("[+] Uploaded PLC program saved as 'plc_program_upload.bin'")
                else:
                    print("[-] Failed to retrieve the program.")
            else:
                print("[-] Failed to connect to the PLC.")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    network_subnet = "192.168.1."  # Change this based on your network
    plc_ip = discover_plc(network_subnet)
    
    if plc_ip:
        upload_plc_program(plc_ip)
    else:
        print("[-] No PLC found on the network.")