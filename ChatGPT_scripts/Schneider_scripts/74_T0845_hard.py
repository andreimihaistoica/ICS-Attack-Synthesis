import socket
import os
from pyModbusTCP.client import ModbusClient

# Step 1: Find the PLC's IP Address
def find_plc_ip(subnet="192.168.9"):
    print("Scanning network for PLC...")
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            # Create a socket to test Modbus TCP communication (Port 502)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Set connection timeout
            sock.connect((ip, 502))  # Check if Modbus TCP port is open
            print(f"PLC found at IP: {ip}")
            sock.close()
            return ip
        except:
            pass  # Ignore unreachable IPs
    print("No PLC found on the subnet.")
    return None

# Step 2: Upload the Program from the PLC
def upload_program(plc_ip, modbus_client_id=1, output_file="uploaded_program.txt"):
    print(f"Connecting to PLC at {plc_ip}...")

    # Modbus client setup
    client = ModbusClient(host=plc_ip, port=502, unit_id=modbus_client_id, auto_open=True)

    if client.open():
        print("Connected to PLC via Modbus TCP.")
        try:
            # Assuming program is stored in specific memory regions - simulation only
            print("Attempting to read PLC memory for program logic...")

            # Example memory addresses (could vary depending on PLC hardware)
            start_address = 0x0000  # Adjust to actual memory map for program logic
            num_registers = 125  # Number of registers to read per request

            with open(output_file, "w") as output:
                for block in range(10):  # Read 10 blocks of 125 registers (example)
                    address = start_address + (block * num_registers)
                    registers = client.read_holding_registers(address, num_registers)
                    if registers:
                        output.write(f"Registers @ {hex(address)}: {registers}\n")
                        print(f"Read block {block + 1}: Registers @ {hex(address)} written to file.")
                    else:
                        print(f"Failed to read registers @ {hex(address)}")
                        break

            print(f"Program successfully uploaded and saved to {output_file}.")
        except Exception as e:
            print(f"Error during program upload: {e}")
        finally:
            client.close()
    else:
        print("Failed to connect to PLC.")
        return False

    return True


# Putting it all together
def main():
    # Network and PLC configuration
    subnet = "192.168.9"  # Adjust if the subnet is different
    program_output_file = "uploaded_program.txt"

    # Step 1: Find PLC IP
    plc_ip = find_plc_ip(subnet=subnet)
    if not plc_ip:
        print("Could not locate PLC on the network.")
        return

    # Step 2: Upload PLC program
    success = upload_program(plc_ip, output_file=program_output_file)
    if success:
        print(f"PLC program uploaded successfully to {program_output_file}.")
    else:
        print("Failed to upload PLC program.")


if __name__ == "__main__":
    main()