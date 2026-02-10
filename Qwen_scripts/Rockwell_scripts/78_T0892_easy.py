import netmiko
import scapy.all as scapy
import time

# Function to scan the network and find the PLC's IP address
def scan_network():
    print("Scanning network for PLC...")
    ip_range = "192.168.1.0/24"  # Change this to your network range
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    for element in answered_list:
        print(f"IP: {element[1].psrc} - MAC: {element[1].hwsrc}")
        # Assuming the PLC has a specific MAC address or other identifier
        if element[1].hwsrc == "00:11:22:33:44:55":  # Change this to the PLC's MAC address
            return element[1].psrc
    return None

# Function to change the PLC's credentials
def change_plc_credentials(ip, username, password, new_password):
    try:
        print(f"Connecting to PLC at {ip}...")
        device = {
            'device_type': 'cisco_ios',  # Change this to the appropriate device type
            'ip': ip,
            'username': username,
            'password': password,
        }

        connection = netmiko.ConnectHandler(**device)
        print("Connected to PLC.")

        # Change the password
        print("Changing credentials...")
        connection.send_command_timing("enable")
        connection.send_command_timing("configure terminal")
        connection.send_command_timing(f"username {username} secret {new_password}")
        connection.send_command_timing("end")
        connection.send_command_timing("write memory")

        print("Credentials changed successfully.")
        connection.disconnect()
    except Exception as e:
        print(f"Failed to change credentials: {e}")

# Main function
def main():
    # Initial credentials
    username = "admin"  # Change this to the actual username
    password = "password"  # Change this to the actual password
    new_password = "new_secure_password"  # Change this to the new password

    # Find the PLC's IP address
    plc_ip = scan_network()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        # Change the PLC's credentials
        change_plc_credentials(plc_ip, username, password, new_password)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()