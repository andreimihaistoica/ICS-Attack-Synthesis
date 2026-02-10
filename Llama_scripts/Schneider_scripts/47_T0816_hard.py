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

# Define the Modbus address of the restart/shutdown command
restart_shutdown_address = 0x0000  # Replace with the actual address of the restart/shutdown command

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

def restart_plc():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    from pymodbus.client.sync import ModbusTcpClient
    client = ModbusTcpClient(plc_ip, plc_port)
    # Send the restart command to the PLC
    client.write_coil(restart_shutdown_address, 0xFF00)

def shutdown_plc():
    global plc_ip
    # Use the pymodbus library to access the PLC's memory regions
    from pymodbus.client.sync import ModbusTcpClient
    client = ModbusTcpClient(plc_ip, plc_port)
    # Send the shutdown command to the PLC
    client.write_coil(restart_shutdown_address, 0x0000)

def main():
    global plc_ip
    # Find the PLC's IP address
    find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network")
        return
    # Restart or shutdown the PLC
    while True:
        print("1. Restart PLC")
        print("2. Shutdown PLC")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            restart_plc()
            print("PLC restarted")
        elif choice == "2":
            shutdown_plc()
            print("PLC shutdown")
        elif choice == "3":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()