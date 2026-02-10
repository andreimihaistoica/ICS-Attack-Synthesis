from pycomm3 import LogixDriver
import subprocess
import re

def find_plc_ip():
    # Use ARP scan to find devices on the network (adjust the network interface if necessary)
    result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)
    arp_output = result.stdout.decode('utf-8')
    
    # Regex to find IP addresses in the ARP table
    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    ip_addresses = ip_pattern.findall(arp_output)
    
    # Iterate through IP addresses to find the PLC (this is a simple example, adjust as needed)
    for ip in ip_addresses:
        try:
            with LogixDriver(ip) as plc:
                if plc.get_plc_name():  # Check if the device is a PLC
                    return ip
        except:
            continue
    return None

def restart_plc(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Send a command to restart the PLC (this is a placeholder, adjust based on your PLC's capabilities)
            # Note: This is a destructive action and should only be done in controlled environments.
            plc.write('START', False)  # Example: Reset the START variable to False
            plc.write('STOP', True)    # Example: Set the STOP variable to True
            print(f"Restart command sent to PLC at {plc_ip}")
    except Exception as e:
        print(f"Failed to restart PLC: {e}")

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        restart_plc(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()