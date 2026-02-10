import socket
import subprocess
import pymodbus.client.sync as modbus_client
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use ARP scan to find devices on the network
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    for line in lines:
        if 'dynamic' in line:
            ip = line.split()[0]
            try:
                # Attempt to connect to the IP address to see if it's the PLC
                client = modbus_client.ModbusTcpClient(ip)
                client.connect()
                if client.is_socket_open():
                    print(f"PLC found at IP: {ip}")
                    client.close()
                    return ip
            except Exception as e:
                print(f"Failed to connect to {ip}: {e}")
                continue
    return None

# Function to upload the program from the PLC
def upload_program_from_plc(plc_ip):
    try:
        client = modbus_client.ModbusTcpClient(plc_ip)
        client.connect()
        
        if not client.is_socket_open():
            print("Failed to connect to the PLC.")
            return
        
        # Example: Read holding registers (this is a placeholder for the actual program upload logic)
        # In a real scenario, you would use the appropriate function to read the program data
        start_address = 0
        count = 100  # Number of registers to read
        response = client.read_holding_registers(start_address, count, unit=1)
        
        if response.isError():
            print("Error reading registers from the PLC.")
        else:
            print("Program data read from the PLC:")
            print(response.registers)
        
        client.close()
    except Exception as e:
        print(f"Error uploading program from PLC: {e}")

# Main function
def main():
    print("Starting PLC program upload script...")
    
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network.")
        return
    
    # Upload the program from the PLC
    upload_program_from_plc(plc_ip)

if __name__ == "__main__":
    main()