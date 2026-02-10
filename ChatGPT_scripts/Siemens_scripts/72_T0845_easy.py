import socket
import struct
import subprocess
from pycomm3 import LogixDriver  # For Rockwell PLCs
from pymodbus.client import ModbusTcpClient  # For Modbus-based PLCs


def find_plc_ip(network_prefix="192.168.1"):
    """Scan for active devices in the network to find the PLC."""
    found_ips = []
    
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        try:
            result = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                found_ips.append(ip)
        except Exception as e:
            print(f"Error scanning IP {ip}: {e}")

    # Check which IP could be the PLC (using a simple Modbus connection test)
    for ip in found_ips:
        client = ModbusTcpClient(ip)
        if client.connect():
            print(f"PLC Detected at Modbus Address: {ip}")
            client.close()
            return ip

        # If not found via Modbus, check Rockwell's CLS discovery
        try:
            with LogixDriver(ip) as plc:
                print(f"PLC identified (Rockwell) at IP: {ip}")
                return ip
        except:
            continue

    print("No PLC found in the network!")
    return None


def upload_program_modbus(plc_ip):
    """Upload PLC program via Modbus (if supported)."""
    client = ModbusTcpClient(plc_ip)
    
    if client.connect():
        print(f"Connected to PLC at {plc_ip} via Modbus.")
        
        # Assuming the vendor supports memory reading via Modbus
        response = client.read_holding_registers(0, 125)
        if response:
            print("Reading PLC Program Data (first 125 registers):")
            print(response.registers)

            # Save to file
            with open("plc_program_dump_modbus.txt", "w") as file:
                file.write(str(response.registers))
            
            print("Program uploaded and saved (via Modbus).")
        else:
            print("Failed to read PLC memory.")
        
        client.close()
    else:
        print(f"Failed to connect to PLC at {plc_ip}.")


def upload_program_rockwell(plc_ip):
    """Upload PLC program from Rockwell PLC using LogixDriver."""
    try:
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to Rockwell PLC at {plc_ip}.")
            program_data = plc.get_tag_list()
            
            if program_data:
                with open("plc_program_dump_rockwell.txt", "w") as file:
                    for tag in program_data:
                        file.write(f"{tag}\n")
                print("PLC program uploaded and saved.")
            else:
                print("Failed to upload PLC program.")
    except Exception as e:
        print(f"Error connecting to PLC: {e}")


if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        # Try Rockwell first, then Modbus
        try:
            upload_program_rockwell(plc_ip)
        except:
            upload_program_modbus(plc_ip)