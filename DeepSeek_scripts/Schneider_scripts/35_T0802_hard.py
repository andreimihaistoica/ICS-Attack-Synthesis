import socket
from pymodbus.client.sync import ModbusTcpClient

def find_plc_ip(subnet):
    """Scan the subnet to find the PLC's IP address."""
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                if s.connect_ex((ip, 502)) == 0:
                    print(f"Found PLC at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    return None

def collect_plc_data(ip):
    """Collect data from the PLC using Modbus protocol."""
    try:
        client = ModbusTcpClient(ip)
        if client.connect():
            print("Connected to PLC")

            # Read coils (digital outputs)
            coils = client.read_coils(0, 8)
            if not coils.isError():
                print("Coils (Digital Outputs):", coils.bits)

            # Read discrete inputs (digital inputs)
            inputs = client.read_discrete_inputs(0, 8)
            if not inputs.isError():
                print("Discrete Inputs (Digital Inputs):", inputs.bits)

            # Read holding registers (memory bits, timers, counters)
            registers = client.read_holding_registers(0, 16)
            if not registers.isError():
                print("Holding Registers (Memory Bits, Timers, Counters):", registers.registers)

            client.close()
        else:
            print("Failed to connect to PLC")
    except Exception as e:
        print(f"Error collecting data from PLC: {e}")

if __name__ == "__main__":
    subnet = "192.168.9"
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        collect_plc_data(plc_ip)
    else:
        print("PLC not found on the network.")