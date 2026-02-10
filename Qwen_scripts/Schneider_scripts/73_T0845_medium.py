import socket
import struct
import time
from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range (e.g., 192.168.1.0/24)
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if received.psrc != "192.168.1.1":  # Exclude the gateway
            print(f"Found device: {received.psrc}")
            return received.psrc
    
    print("PLC not found on the network.")
    return None

# Function to upload the program from the PLC
def upload_program_from_plc(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        client.connect()
        
        # Define the starting address and number of registers to read
        start_address = 0
        num_registers = 100  # Adjust this based on the program size
        
        # Read the program data from the PLC
        response = client.read_holding_registers(start_address, num_registers, unit=1)
        
        if response.isError():
            print("Error reading registers from the PLC.")
            return
        
        # Extract the program data
        program_data = response.registers
        
        # Save the program data to a file
        with open("plc_program.txt", "w") as file:
            for register in program_data:
                file.write(f"{register}\n")
        
        print("Program uploaded successfully and saved to plc_program.txt.")
    
    except ModbusIOException as e:
        print(f"Modbus IO Exception: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Upload the program from the PLC
        upload_program_from_plc(plc_ip)

if __name__ == "__main__":
    main()