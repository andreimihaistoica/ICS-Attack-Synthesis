import nmap
from pymodbus.client.sync import ModbusTcpClient
import time

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-p 502')  # Modbus TCP port is 502
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

# Function to read the I/O Image from the PLC
def read_io_image(plc_ip):
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return None

    try:
        # Read input registers (0x0000 - 0x00FF)
        input_registers = client.read_input_registers(0, 256, unit=1)
        if input_registers.isError():
            print("Failed to read input registers")
            return None

        # Read holding registers (0x0000 - 0x00FF)
        holding_registers = client.read_holding_registers(0, 256, unit=1)
        if holding_registers.isError():
            print("Failed to read holding registers")
            return None

        return input_registers.registers, holding_registers.registers
    finally:
        client.close()

# Main function
def main():
    subnet = '192.168.1.0/24'  # Change this to your network subnet
    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        input_image, output_image = read_io_image(plc_ip)
        if input_image and output_image:
            print("Input Image (Input Registers):", input_image)
            print("Output Image (Holding Registers):", output_image)
        else:
            print("Failed to read I/O Image")
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()