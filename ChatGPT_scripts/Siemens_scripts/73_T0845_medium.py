import snap7
import socket
import struct
import time

# Function to scan for Siemens PLCs in the local network
def discover_plc():
    print("[+] Scanning network for Siemens S7-1200 PLC...")
    
    plc_ip_range = "192.168.0."  # Adjust to match the network segment
    for i in range(1, 255):
        potential_ip = f"{plc_ip_range}{i}"
        try:
            client = snap7.client.Client()
            client.connect(potential_ip, 0, 1)
            if client.get_connected():
                print(f"[+] PLC Found at {potential_ip}")
                client.disconnect()
                return potential_ip
        except:
            continue
    
    print("[-] No PLC found on the network.")
    return None

# Function to upload and retrieve program blocks from the PLC
def upload_program(plc_ip):
    print(f"[+] Connecting to PLC at {plc_ip}...")
    
    try:
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)

        if client.get_connected():
            print("[+] Successfully connected to PLC.")

            # Attempt to read program block (DB1 as an example)
            db_number = 1  
            db_size = 256  # Adjust based on expected program size

            print(f"[+] Uploading program block DB{db_number} from PLC...")
            
            data = client.db_read(db_number, 0, db_size)
            
            print(f"[+] Successfully extracted program block DB{db_number}.")
            
            # Save uploaded program to a file
            with open(f"PLC_Program_DB{db_number}.bin", "wb") as f:
                f.write(data)
            
            print(f"[+] Program saved as 'PLC_Program_DB{db_number}.bin'")

        client.disconnect()

    except Exception as e:
        print(f"[-] Error uploading program: {e}")

if __name__ == "__main__":
    plc_ip = discover_plc()
    
    if plc_ip:
        upload_program(plc_ip)
    else:
        print("[-] No PLC detected. Exiting...")