import nmap

def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 102')  # Scan the local network for port 102 (S7 protocol)
    for host in nm.all_hosts():
        if nm[host].has_tcp(102) and nm[host]['tcp'][102]['state'] == 'open':
            return host
    return None

plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC found at IP: {plc_ip}")
else:
    print("PLC not found")