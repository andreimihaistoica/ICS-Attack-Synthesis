from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import sys

# Define the PLC's IP address and port
PLC_IP = "192.168.1.10"  # Replace with the actual IP address of the PLC
PLC_PORT = 502

# Function to detect the PLC's operating mode
def detect_operating_mode(client):
    try:
        # Read the operating mode from the PLC
        # The address and length may vary depending on the PLC model and configuration
        # Consult the PLC's documentation for the correct address
        response = client.read_holding_registers(address=0, count=1, slave=1)
        
        if response.isError():
            print("Error reading from the PLC.")
            return None
        
        # The operating mode is typically stored in the first register
        operating_mode = response.registers[0]
        
        # Map the operating mode value to its corresponding mode
        if operating_mode == 0:
            return "Program"
        elif operating_mode == 1:
            return "Run"
        elif operating_mode == 2:
            return "Remote"
        elif operating_mode == 3:
            return "Stop"
        elif operating_mode == 4:
            return "Reset"
        elif operating_mode == 5:
            return "Test / Monitor"
        else:
            return "Unknown"
    
    except ModbusException as e:
        print(f"Modbus error: {e}")
        return None

# Main function
def main():
    # Create a Modbus TCP client
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    
    # Connect to the PLC
    if client.connect():
        print(f"Connected to PLC at {PLC_IP}:{PLC_PORT}")
        
        # Detect the operating mode
        mode = detect_operating_mode(client)
        if mode:
            print(f"PLC Operating Mode: {mode}")
        else:
            print("Could not detect the operating mode.")
        
        # Disconnect from the PLC
        client.close()
    else:
        print(f"Could not connect to PLC at {PLC_IP}:{PLC_PORT}")

if __name__ == "__main__":
    main()