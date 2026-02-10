import snap7
import socket
import struct
import os

def find_plc_ip(subnet="192.168.1."):
    """
    Scans for the PLC's IP address in the subnet by checking common Siemens PLC ports.
    """
    plc_ports = [102]  # Port 102 is commonly used for Siemens S7comm.
    
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        for port in plc_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Set timeout for better scanning performance.
            try:
                sock.connect((ip, port))
                print(f"[+] PLC Found at: {ip}")
                sock.close()
                return ip
            except (socket.timeout, ConnectionRefusedError):
                pass
            finally:
                sock.close()

    print("[-] No PLC found in the subnet.")
    return None

def connect_plc(ip):
    """
    Connects to the PLC and retrieves basic information.
    """
    plc = snap7.client.Client()
    try:
        plc.connect(ip, 0, 1)  # Rack: 0, Slot: 1 (common Siemens setup)
        print("[+] Connected to PLC:", ip)
        
        # Read PLC state
        state = plc.get_cpu_state()
        print(f"[+] PLC state: {state}")

        if state != "RUN":
            print("[!] PLC is not in RUN mode. Changing to RUN mode (if possible).")
            plc.plc_hot_start()  # Start without program reloading

        return plc
    except Exception as e:
        print(f"[-] Connection to PLC failed: {e}")
        return None

def program_download(plc, filepath):
    """
    Simulates downloading an updated program to the PLC.
    """
    if not os.path.exists(filepath):
        print("[-] Program file not found!")
        return

    try:
        with open(filepath, "rb") as f:
            program_data = f.read()

        print("[+] Loading program into PLC memory...")
        
        # This function is highly vendor-specific.
        # In Snap7, we typically use DB upload/download but for actual logic code uploads, 
        # vendor SDKs (like TIA Portal APIs) are needed.
        plc.download(program_data)  # This function assumes a valid binary for the PLC

        print("[+] Program download complete!")
    except Exception as e:
        print(f"[-] Failed to download program: {e}")

def main():
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Aborting due to failure in discovering PLC IP.")
        return

    plc = connect_plc(plc_ip)
    if not plc:
        print("Aborting due to failure connecting to PLC.")
        return

    # Provide the compiled PLC program file (binary format)
    program_path = "updated_program.bin"  # This should be your program's binary file
    program_download(plc, program_path)

    plc.disconnect()  # Always disconnect after operation
    print("[+] PLC interaction complete.")

if __name__ == "__main__":
    main()