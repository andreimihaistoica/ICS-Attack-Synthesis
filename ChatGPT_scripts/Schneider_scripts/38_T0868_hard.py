from pymodbus.client.sync import ModbusTcpClient
import socket
import ipaddress


def find_device_ip(start_ip, subnet_mask, port=502):
    """
    Discover the PLC's IP address in the given range by attempting to connect on the Modbus TCP port.
    """
    print("Searching for PLC on the network...")
    subnet = ipaddress.IPv4Network(f"{start_ip}/{subnet_mask}", strict=False)
    for ip in subnet.hosts():
        try:
            client = ModbusTcpClient(str(ip), port=port)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return str(ip)
        except Exception:
            continue
    print("Unable to locate the PLC.")
    return None


def read_operating_mode(ip, port=502):
    """
    Communicate with the PLC to read its current operating mode.
    """
    try:
        client = ModbusTcpClient(ip, port=port)
        if not client.connect():
            print("Failed to connect to the PLC.")
            return None

        print("Connected to the PLC. Querying operating mode...")

        # Schneider Electric PLCs often store operating mode in specific memory locations.
        # This specific query (reference `0x0025`) may vary based on the PLC. Adjust as required:
        # For TM221CE16R, operational mode address might map to Modbus registers (0x0025 - hypothetical).
        result = client.read_holding_registers(37, 1, unit=1)  # Replace 37 with the actual address for operational mode.
        if result.isError():
            print("Error reading operating mode from the PLC.")
        else:
            mode_value = result.registers[0]
            mode = {
                0: "STOP",
                1: "RUN",
                2: "PROGRAM",
                3: "TEST/MONITOR",
                4: "RESET",
                5: "REMOTE"
            }.get(mode_value, "UNKNOWN")
            print(f"Current Operating Mode: {mode}")
            return mode
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


def main():
    # Define the subnet to scan and the Modbus port
    start_ip = "192.168.9.0"
    subnet_mask = "255.255.255.0"
    modbus_port = 502

    print("Step 1: Discovering PLC IP Address...")
    ip_address = find_device_ip(start_ip, subnet_mask, modbus_port)
    if not ip_address:
        print("PLC not found. Exiting.")
        return

    print("\nStep 2: Determining PLC Operating Mode...")
    operating_mode = read_operating_mode(ip_address, modbus_port)
    if operating_mode:
        print(f"\nSuccessfully determined the PLC operating mode: {operating_mode}")
    else:
        print("\nFailed to determine the PLC operating mode.")


if __name__ == "__main__":
    main()