import netifaces as ni
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    interfaces = ni.interfaces()
    for interface in interfaces:
        addrs = ni.ifaddresses(interface)
        if ni.AF_INET in addrs:
            for link in addrs[ni.AF_INET]:
                ip = link['addr']
                if ip.startswith('192.168.9.'):
                    # Try to connect to the PLC
                    client = ModbusTcpClient(ip)
                    try:
                        client.connect()
                        if client.is_socket_open():
                            print(f"PLC found at IP: {ip}")
                            return ip
                    except ConnectionException:
                        continue
                    finally:
                        client.close()
    print("PLC not found on the network.")
    return None

# Function to read PLC registers
def read_plc_registers(plc_ip):
    client = ModbusTcpClient(plc_ip)
    try:
        client.connect()
        if client.is_socket_open():
            # Read digital inputs
            response = client.read_discrete_inputs(0, 9, unit=1)
            if response.isError():
                print("Error reading digital inputs.")
            else:
                print("Digital Inputs:")
                for i, value in enumerate(response.bits):
                    print(f"Input %I0.{i}: {value}")

            # Read digital outputs
            response = client.read_coils(0, 6, unit=1)
            if response.isError():
                print("Error reading digital outputs.")
            else:
                print("Digital Outputs:")
                for i, value in enumerate(response.bits):
                    print(f"Output %Q0.{i}: {value}")

            # Read memory bits
            response = client.read_discrete_inputs(1, 2, unit=1)
            if response.isError():
                print("Error reading memory bits.")
            else:
                print("Memory Bits:")
                for i, value in enumerate(response.bits):
                    print(f"Memory %M{1 + i}: {value}")

            # Read system bits
            response = client.read_discrete_inputs(6, 1, unit=1)
            if response.isError():
                print("Error reading system bits.")
            else:
                print("System Bits:")
                for i, value in enumerate(response.bits):
                    print(f"System %S{6 + i}: {value}")

            # Read timers
            response = client.read_holding_registers(0, 2, unit=1)
            if response.isError():
                print("Error reading timers.")
            else:
                print("Timers:")
                for i, value in enumerate(response.registers):
                    print(f"Timer %TM{i}: {value}")

            # Read counters
            response = client.read_holding_registers(2, 1, unit=1)
            if response.isError():
                print("Error reading counters.")
            else:
                print("Counters:")
                for i, value in enumerate(response.registers):
                    print(f"Counter %C{i + 2}: {value}")

    except ConnectionException:
        print("Connection to PLC failed.")
    finally:
        client.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        read_plc_registers(plc_ip)

if __name__ == "__main__":
    main()