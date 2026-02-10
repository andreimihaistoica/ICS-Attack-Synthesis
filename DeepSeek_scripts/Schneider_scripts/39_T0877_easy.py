import socket
from pymodbus.client import ModbusTcpClient
import snap7

def discover_plc_ip():
    # Example: Broadcast a discovery packet to find the PLC's IP address
    # This is a placeholder and may need to be adapted based on the PLC's protocol
    # For example, some PLCs respond to ARP or specific discovery packets
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            # Attempt to connect to the PLC on a known port (e.g., Modbus TCP port 502)
            client = ModbusTcpClient(ip, port=502, timeout=1)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except Exception as e:
            pass
    print("PLC not found in the network.")
    return None

def collect_io_image_modbus(plc_ip):
    # Collect I/O Image using Modbus TCP
    client = ModbusTcpClient(plc_ip, port=502)
    if client.connect():
        # Read input registers (example: read 10 registers starting from address 0)
        input_image = client.read_input_registers(address=0, count=10)
        # Read holding registers (example: read 10 registers starting from address 0)
        output_image = client.read_holding_registers(address=0, count=10)
        client.close()
        return input_image, output_image
    else:
        print("Failed to connect to PLC via Modbus TCP.")
        return None, None

def collect_io_image_s7(plc_ip):
    # Collect I/O Image using S7Comm
    client = snap7.client.Client()
    try:
        client.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (default for Siemens S7 PLCs)
        # Read input area (example: read 10 bytes from input area)
        input_image = client.read_area(snap7.types.Areas.PE, 0, 0, 10)
        # Read output area (example: read 10 bytes from output area)
        output_image = client.read_area(snap7.types.Areas.PA, 0, 0, 10)
        client.disconnect()
        return input_image, output_image
    except Exception as e:
        print(f"Failed to connect to PLC via S7Comm: {e}")
        return None, None

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    # Step 2: Collect the I/O Image state
    # Uncomment the appropriate function based on the PLC's protocol
    input_image, output_image = collect_io_image_modbus(plc_ip)
    # input_image, output_image = collect_io_image_s7(plc_ip)

    if input_image and output_image:
        print("Input Image:", input_image)
        print("Output Image:", output_image)
    else:
        print("Failed to collect I/O Image state.")

if __name__ == "__main__":
    main()