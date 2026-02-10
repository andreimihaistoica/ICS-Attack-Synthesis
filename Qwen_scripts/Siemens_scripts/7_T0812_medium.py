import socket
import struct
import subprocess
import time
from pysnmp.hlapi import *
from pymodbus.client.sync import ModbusTcpClient

# Default credentials for Siemens S7-1200 PLC
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'

# Function to discover the PLC's IP address using SNMP
def discover_plc_ip():
    # Define the SNMP community string and the OID for the IP address
    community = 'public'
    oid = '1.3.6.1.2.1.4.22.1.2'  # IP Address OID

    # Perform an SNMP walk to discover the IP address
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget(('192.168.1.1', 161)),  # Replace with your network's broadcast address
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False
    ):
        if errorIndication:
            print(f"Error: {errorIndication}")
            break
        elif errorStatus:
            print(f"Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            break
        else:
            for varBind in varBinds:
                ip_address = varBind[1].prettyPrint()
                if ip_address.startswith('192.168.1.'):  # Adjust the subnet as needed
                    return ip_address

    return None

# Function to connect to the PLC using default credentials
def connect_to_plc(ip_address):
    try:
        # Create a Modbus TCP client
        client = ModbusTcpClient(ip_address)

        # Connect to the PLC
        if client.connect():
            print(f"Connected to PLC at {ip_address}")
            # Perform actions on the PLC (e.g., read/write registers)
            # Example: Read a register
            result = client.read_holding_registers(0, 1, unit=1)
            if result.isError():
                print("Error reading register")
            else:
                print(f"Register value: {result.registers[0]}")
        else:
            print(f"Failed to connect to PLC at {ip_address}")

        # Close the connection
        client.close()
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        # Connect to the PLC using default credentials
        connect_to_plc(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()