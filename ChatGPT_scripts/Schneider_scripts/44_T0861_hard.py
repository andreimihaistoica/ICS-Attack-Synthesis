from pymodbus.client.sync import ModbusTcpClient
import socket
import ipaddress

def find_plc_on_network(subnet="192.168.9.0/24", port=502):
    """
    Scan the specified subnet to find devices with an open Modbus TCP port (default is 502)
    Returns the first detected device's IP address or None if no device is found.
    """
    print("Scanning network for the PLC...")
    subnet_ips = ipaddress.IPv4Network(subnet, strict=False)
    
    for ip in subnet_ips:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)  # Timeout for each connection attempt
                if s.connect_ex((str(ip), port)) == 0:
                    print(f"PLC found at {ip}")
                    return str(ip)
        except Exception as e:
            pass
    return None

def collect_points_and_tags(plc_ip):
    """
    Connect to the PLC at the provided IP address and collect information about Modbus points and tags.
    """
    # Establish a Modbus TCP connection
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Unable to connect to PLC at {plc_ip}")
        return

    try:
        print(f"Connected to PLC at {plc_ip}. Reading tags and points...")

        # Read digital outputs (%Q, starting at zero)
        print("Fetching Digital Outputs (%Q)...")
        response = client.read_coils(0, 8)  # Assume 8 coils for illustration
        if response.isError():
            print("Failed to read digital outputs")
        else:
            outputs = response.bits
            for i, value in enumerate(outputs):
                print(f"%Q{i}: {value}")

        # Read memory bits (%M, starting at zero)
        print("Fetching Memory Bits (%M)...")
        response = client.read_coils(1, 8)  # Assume 8 memory bits for illustration
        if response.isError():
            print("Failed to read memory bits")
        else:
            memory_bits = response.bits
            for i, value in enumerate(memory_bits):
                print(f"%M{i}: {value}")

        # Read system bits (%S, starting at 6 for SB_TB1S)
        print("Fetching System Bits (%S)...")
        response = client.read_coils(6, 1)  # Reading system bit at %S6
        if response.isError():
            print("Failed to read system bits")
        else:
            print(f"%S6 (SB_TB1S): {response.bits[0]}")

        # Read timer values (%TM)
        print("Fetching Timers (%TM)...")
        # Assume timers are stored sequentially as holding registers starting at address 0
        response = client.read_holding_registers(0, 2)  # Assume 2 registers for timers
        if response.isError():
            print("Failed to read timer values")
        else:
            for i, value in enumerate(response.registers):
                print(f"%TM{i}: {value}")

        # Read counter values (%C)
        print("Fetching Counters (%C)...")
        # Assume counters are stored sequentially as holding registers starting at address 10
        response = client.read_holding_registers(10, 1)  # Assume 1 counter for illustration
        if response.isError():
            print("Failed to read counter values")
        else:
            print(f"%C0: {response.registers[0]}")

        # Read analog inputs (%IW)
        print("Fetching Analog Inputs (%IW)...")
        response = client.read_input_registers(0, 2)  # Assume 2 analog inputs for illustration
        if response.isError():
            print("Failed to read analog inputs")
        else:
            for i, value in enumerate(response.registers):
                print(f"%IW{i}: {value}")

    finally:
        # Disconnect the client
        client.close()
        print("Disconnected from PLC.")

# Main flow
if __name__ == "__main__":
    # Step 1: Find the PLC on the network
    plc_ip = find_plc_on_network()
    if plc_ip is None:
        print("PLC not found on the network.")
    else:
        # Step 2: Collect points and tags from the PLC
        collect_points_and_tags(plc_ip)