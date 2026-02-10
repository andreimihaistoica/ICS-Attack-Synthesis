import nmap
import subprocess

def find_plc_ip(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-p 502')  # Assuming the PLC uses Modbus TCP on port 502
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

def main():
    subnet = '192.168.1.0/24'  # Replace with your network subnet
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()