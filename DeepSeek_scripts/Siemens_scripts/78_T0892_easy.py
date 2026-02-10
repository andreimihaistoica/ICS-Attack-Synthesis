import scapy.all as scapy
import requests

# Function to scan the network and find the PLC's IP address
def find_plc_ip(target_network="192.168.1.0/24"):
    print(f"Scanning network {target_network} for the PLC...")
    arp_request = scapy.ARP(pdst=target_network)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    plc_ip = None
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"Found device: IP={ip}, MAC={mac}")
        # Assuming the PLC has a specific MAC vendor prefix (e.g., Siemens PLCs use 00:1C:06)
        if mac.startswith("00:1C:06"):  # Replace with the actual MAC vendor prefix of your PLC
            plc_ip = ip
            print(f"PLC found at IP: {plc_ip}")
            break

    if not plc_ip:
        print("PLC not found on the network.")
    return plc_ip

# Function to change the PLC's credentials (example API call)
def change_plc_credentials(plc_ip, new_password):
    url = f"http://{plc_ip}/api/change_password"  # Replace with the actual API endpoint
    payload = {"new_password": new_password}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"Successfully changed the PLC's credentials. New password: {new_password}")
        else:
            print(f"Failed to change credentials. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the PLC: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        exit("Cannot proceed without the PLC's IP address.")

    # Step 2: Change the PLC's credentials
    new_password = "NewSecurePassword123"  # Replace with the desired password
    change_plc_credentials(plc_ip, new_password)