import snap7
from snap7.util import get_int
import nmap
import socket

def find_plc_ip(subnet="192.168.1.0/24"):
    """ Scan network to locate the Siemens PLC based on open port 102 (Siemens S7 protocol) """
    nm = nmap.PortScanner()
    print(f"[*] Scanning network {subnet} for Siemens PLC...")
    
    nm.scan(hosts=subnet, arguments='-p 102 --open -sS', timeout=5)
    
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and 102 in nm[host]['tcp']:
            print(f"[+] Siemens PLC found at: {host}")
            return host  # Return the first PLC found

    print("[-] No Siemens PLC found on the network.")
    return None


def upload_s7_program(plc_ip, output_filename="uploaded_program.s7p"):
    """ Connect to the Siemens S7 PLC and upload the current program """
    plc = snap7.client.Client()
    
    try:
        print(f"[*] Connecting to Siemens PLC at {plc_ip}...")
        plc.connect(plc_ip, 0, 1)  # Rack=0, Slot=1 for S7-1200
        
        if plc.get_connected():
            print("[+] Connected to PLC. Uploading Program...")

            # Request PLC memory areas containing program logic
            cpu_info = plc.get_cpu_info()
            print(f"[+] CPU Type: {cpu_info.ModuleTypeName.decode('utf-8')}")

            # Read specific DB Blocks, Code, or Configurations (Targeting OB1 as an example)
            block_num = 1  # OB1, FC blocks may have different numbers
            uploaded_data = plc.upload(block_num)

            # Save uploaded data to file
            with open(output_filename, "wb") as file:
                file.write(uploaded_data)

            print(f"[+] Program successfully uploaded and saved as '{output_filename}'")

        else:
            print("[-] Failed to connect to the PLC.")

    except Exception as e:
        print(f"[!] Error: {e}")

    finally:
        plc.disconnect()


if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip_address = find_plc_ip("192.168.1.0/24")  # Modify subnet if needed

    if plc_ip_address:
        # Step 2: Upload program from PLC
        upload_s7_program(plc_ip_address)