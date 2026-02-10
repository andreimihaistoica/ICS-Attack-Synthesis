from pymodbus.client.sync import ModbusTcpClient
import ipaddress
import time

# Function to identify the PLC on the network
def find_plc_ip(network_prefix):
    print(f"Scanning for PLC on network: {network_prefix}...")
    for ip in ipaddress.IPv4Network(f"{network_prefix}/24"):
        ip = str(ip)
        try:
            client = ModbusTcpClient(ip)
            if client.connect():
                # Example: Check a common address that responds if the PLC is present
                # Reading Coil Status at address 0 to see if it is a valid Modbus device
                response = client.read_coils(0, 1)
                if response.isError():
                    client.close()
                    continue  # Not a valid PLC or not responding on Modbus
                print(f"PLC detected at IP: {ip}")
                client.close()
                return ip
            else:
                client.close()
        except Exception:
            continue
    print("No PLC found on the provided network.")
    return None

# Function to simulate a "program download"
def program_download(plc_ip, port=502):
    print(f"Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip, port)
    if not client.connect():
        print(f"Unable to connect to PLC at {plc_ip}")
        return
    
    print("Connected. Preparing program download...")

    # This part simulates a download by writing specific data to Modbus registers
    # Example: Holding registers, assuming writable memory for configuration change
    try:
        # Switch to STOP mode (requires knowing vendor-specific modes - simulated here)
        print("Stopping the PLC...")
        client.write_coil(1000, True)  # Hypothetical memory bit for "Stop Mode"

        time.sleep(2)  # Allow time for the PLC to transition to STOP mode

        # Write a new program (simulated by writing values to Modbus holding registers)
        print("Writing new program to PLC memory...")
        data = [100, 200, 300, 400, 500]  # Example program data
        for index, value in enumerate(data):
            address = 4000 + index  # Example memory address range for program
            client.write_register(address, value)
            print(f"Written {value} to register address {address}")

        # Switch to RUN mode (hypothetical)
        print("Restarting the PLC in RUN mode...")
        client.write_coil(1001, True)  # Hypothetical memory bit for "Run Mode"

        print("Program download completed successfully.")

    except Exception as e:
        print(f"Error during program download: {e}")
    finally:
        client.close()

# Main script logic
if __name__ == '__main__':
    # Step 1: Find the PLC IP Address
    network_prefix = "192.168.9.0"  # Example: Adjust this for your specific network
    plc_ip = find_plc_ip(network_prefix)
    
    if plc_ip:
        # Step 2: Perform the Program Download
        program_download(plc_ip)
    else:
        print("PLC could not be found on the network. Exiting.")