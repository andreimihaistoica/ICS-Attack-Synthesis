import nmap

def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 502')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

plc_ip = find_plc_ip()
if plc_ip:
    print(f"PLC IP Address: {plc_ip}")
else:
    print("PLC not found on the network.")