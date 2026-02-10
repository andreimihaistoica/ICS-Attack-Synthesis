import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Defaults

# Define subnet configuration for IP scanning
SUBNET = "192.168.9."  # Modify this according to the network containing the PLC
PORT = 502             # Default port for Modbus communication
PLC_IP = None          # Placeholder to identify the PLC IP

def find_plc_ip():
    """Scan the subnet for the PLC IP address using Modbus communication."""
    global PLC_IP
    print(f"Scanning subnet {SUBNET} for PLC...")
    for i in range(1, 255):  # Scan all IPs in the subnet range
        ip = f"{SUBNET}{i}"
        try:
            client = ModbusTcpClient(ip, port=PORT)
            client.connect()

            # Check if the system responds to any Modbus request as a quick test
            result = client.read_coils(0, 1)  # Attempt to read the first coil
            if result.isError():
                client.close()
                continue  # If there's an error, skip this IP
            
            # If no error, assume we found a Modbus-compatible device (likely the PLC)
            print(f"PLC detected at IP: {ip}")
            PLC_IP = ip
            client.close()
            break
        except:
            continue
    if PLC_IP is None:
        print("PLC not found on the subnet.")
        exit(1)

def collect_plc_data(ip):
    """Automate collection of the PLC's information using the Modbus protocol."""
    print(f"Connecting to PLC at {ip}...")
    client = ModbusTcpClient(ip, port=PORT)
    if not client.connect():
        print("Failed to connect to the PLC.")
        exit(1)

    try:
        # Example automated collection tasks - more can be added as needed

        # 1. Read Digital Outputs (Coils)
        print("\nCollecting Digital Outputs (%Q):")
        digital_outputs = client.read_coils(0, 8)  # Assuming up to 8 coils
        if not digital_outputs.isError():
            for i, status in enumerate(digital_outputs.bits):
                print(f"  Digital Output %Q0.{i}: {'ON' if status else 'OFF'}")
        
        # 2. Read Memory Bits (%M)
        print("\nCollecting Memory Bits (%M):")
        memory_bits = client.read_coils(1, 16)  # Assuming 16 memory bits (%M1 to %M16)
        if not memory_bits.isError():
            for i, status in enumerate(memory_bits.bits):
                print(f"  Memory Bit %M{i+1}: {'ON' if status else 'OFF'}")
        
        # 3. Read Analog Inputs (%IW)
        print("\nCollecting Analog Inputs (%IW):")
        analog_inputs = client.read_input_registers(0, 2)  # Assuming 2 analog input registers
        if not analog_inputs.isError():
            for i, value in enumerate(analog_inputs.registers):
                print(f"  Analog Input %IW0.{i}: {value}")
        
        # 4. Read Timers and Counters
        print("\nCollecting Timer and Counter data:")
        timers = client.read_holding_registers(100, 2)  # Adjust address according to configuration
        if not timers.isError():
            print(f"  Timer 0 Current Value: {timers.registers[0]}")
            print(f"  Timer 1 Current Value: {timers.registers[1]}")
        
        counters = client.read_holding_registers(200, 1)  # Adjust address for counters
        if not counters.isError():
            print(f"  Counter 0 Value: {counters.registers[0]}")
        
        # 5. Collect System Bits
        print("\nCollecting System Bits (%S):")
        system_bits = client.read_coils(6, 1)  # %S6: 1-second Time Base
        if not system_bits.isError():
            print(f"  System Bit %S6 (1-Second Time Base): {'ON' if system_bits.bits[0] else 'OFF'}")
    except Exception as e:
        print(f"Error during data collection: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    find_plc_ip()
    
    # Step 2: Automate collection of data
    if PLC_IP:
        collect_plc_data(PLC_IP)