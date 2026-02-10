from pymodbus.client import ModbusTcpClient
import socket
import ipaddress

# Function to scan the network for the PLC's IP address
def find_plc_ip(subnet):
    for ip in ipaddress.IPv4Network(subnet):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex((str(ip), 502)) == 0:
                    return str(ip)
        except Exception as e:
            continue
    return None

# Function to collect points and tags from the PLC
def collect_points_and_tags(ip):
    client = ModbusTcpClient(ip)
    client.connect()

    # Collect digital inputs
    digital_inputs = client.read_discrete_inputs(0, 8)
    print("Digital Inputs:")
    for i in range(8):
        print(f"%I0.{i}: {digital_inputs.bits[i]}")

    # Collect digital outputs
    digital_outputs = client.read_coils(0, 8)
    print("\nDigital Outputs:")
    for i in range(8):
        print(f"%Q0.{i}: {digital_outputs.bits[i]}")

    # Collect memory bits
    memory_bits = client.read_coils(1, 2)
    print("\nMemory Bits:")
    print(f"%M1 (M_ACTFAN): {memory_bits.bits[0]}")
    print(f"%M2 (M_TOG): {memory_bits.bits[1]}")

    # Collect system bits
    system_bits = client.read_discrete_inputs(6, 1)
    print("\nSystem Bits:")
    print(f"%S6 (SB_TB1S): {system_bits.bits[0]}")

    # Collect counters
    counter = client.read_holding_registers(0, 1)
    print("\nCounters:")
    print(f"%C0 (Counter0): {counter.registers[0]}")

    # Collect timers
    timer0 = client.read_holding_registers(0, 1)
    timer1 = client.read_holding_registers(1, 1)
    print("\nTimers:")
    print(f"%TM0 (Timer0): {timer0.registers[0]}")
    print(f"%TM1 (Timer1): {timer1.registers[1]}")

    client.close()

# Main script
if __name__ == "__main__":
    subnet = "192.168.9.0/24"  # Adjust the subnet as needed
    plc_ip = find_plc_ip(subnet)

    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        collect_points_and_tags(plc_ip)
    else:
        print("PLC not found on the network.")