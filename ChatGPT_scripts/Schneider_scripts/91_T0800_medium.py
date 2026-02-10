from pymodbus.client.sync import ModbusTcpClient
import socket
import ipaddress

# General Configuration
PLC_PORT = 502  # Default Modbus TCP port
BROADCAST_IP = "192.168.0.255/24"  # Replace with your network's broadcast/subnet mask
FIRMWARE_UPDATE_REGISTER = 40001  # Example memory register for firmware update
FIRMWARE_UPDATE_COMMAND = 0x1234  # Hypothetical value to activate firmware update mode

# Step 1: Function to discover PLC in the network (via port scanning)
def find_plc_ip(subnet):
    print("[*] Scanning network for PLC...")
    found_plc = None

    for ip in ipaddress.IPv4Network(subnet, strict=False):
        ip_str = str(ip)
        try:
            print(f"[*] Checking {ip_str}...")
            client = ModbusTcpClient(ip_str, port=PLC_PORT)
            if client.connect():
                print(f"[+] PLC found at {ip_str}")
                found_plc = ip_str
                client.close()
                break
            client.close()
        except Exception as e:
            # Handle any errors or invalid IPs
            print(f"[-] Could not reach {ip_str}: {e}")

    if not found_plc:
        print("[-] No PLC found in the network.")
    return found_plc

# Step 2: Activate firmware update mode
def activate_firmware_update_mode(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip, port=PLC_PORT)

    if client.connect():
        print(f"[+] Connected to PLC at {plc_ip}")
        print("[*] Attempting to activate firmware update mode...")
        try:
            # Write the firmware update command to a specific register
            response = client.write_register(FIRMWARE_UPDATE_REGISTER, FIRMWARE_UPDATE_COMMAND)
            
            if response.isError():
                print("[-] Failed to activate firmware update mode.")
            else:
                print("[+] Firmware update mode activated. NOTE: Ensure new firmware is uploaded or device functionality may be impaired.")

        except Exception as e:
            print(f"[-] Error: {e}")
        finally:
            client.close()
    else:
        print(f"[-] Could not connect to PLC at {plc_ip}.")

if __name__ == "__main__":
    # Step 1: Discover PLC IP
    plc_ip = find_plc_ip(BROADCAST_IP)
    
    # Step 2: Activate firmware update mode if the PLC is found
    if plc_ip:
        activate_firmware_update_mode(plc_ip)
    else:
        print("[!] Failed to find PLC on the network.")