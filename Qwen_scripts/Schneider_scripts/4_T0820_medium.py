import nmap
import requests

# Function to scan the network and find the PLC
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 502')  # Scan for Modbus TCP on port 502
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

# Function to check for known vulnerabilities
def check_vulnerabilities(ip):
    # Example: Check for a known vulnerability using a web API
    url = f"https://vulnerability-checker.example.com/api/v1/check?ip={ip}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        vulnerabilities = check_vulnerabilities(plc_ip)
        if vulnerabilities:
            print("Vulnerabilities found:")
            for vuln in vulnerabilities:
                print(vuln)
        else:
            print("No known vulnerabilities found.")
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()