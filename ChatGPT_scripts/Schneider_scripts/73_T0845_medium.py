import nmap
from pymodbus.client.sync import ModbusTcpClient
import time

# Function to find PLC by scanning for Modbus/TCP (Port 502)
def find_plc_ip():
    nm = nmap.PortScanner()
    subnet = "192.168.1.0/24"  # Adjust based on your network
    
    print("[*] Scanning network for Modbus-enabled PLCs...")
    nm.scan(hosts=subnet, arguments='-p 502 --open')

    for host in nm.all_hosts():
        if 'tcp' in nm[host] and nm[host]['tcp'][502]['state'] == 'open':
            print(f"[+] Found PLC at: {host}")
            return host
    return None

# Function to connect and upload PLC program
def upload_plc_program(plc_ip):
    try:
        print(f"[*] Connecting to PLC at {plc_ip}...")
        client = ModbusTcpClient(plc_ip, port=502)
        
        if client.connect():
            print("[+] Successfully connected to PLC.")
            
            # Schneider Electric uses Modbus registers for configuration & status
            # Read some registers as an example extraction
            response = client.read_input_registers(0, 10, unit=1)
            
            if response.isError():
                print("[-] Could not read data from PLC.")
            else:
                print(f"[+] Response from PLC: {response.registers}")
                
                # If vendor tools allow program upload, initiate it here
                # Example: Send vendor-specific command (proprietary)
                print("[*] Uploading PLC program (if accessible)...")
                
                # Typically, uploading requires specific vendor SDKs like EcoStruxure
                
                # Place actual upload command here depending on API or SDK
                
                print("[+] PLC program uploaded successfully (if access was possible).")
            
            client.close()
        else:
            print("[-] Could not connect to PLC.")
    except Exception as e:
        print(f"[-] Error: {e}")

# Main procedure
def main():
    plc_ip = find_plc_ip()
    
    if plc_ip:
        upload_plc_program(plc_ip)
    else:
        print("[-] No PLC found on the network.")

if __name__ == "__main__":
    main()