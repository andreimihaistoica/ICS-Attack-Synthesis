from pymodbus.client import ModbusTcpClient
import socket
import time

def find_plc_ip(target_ip_range="192.168.9.0/24"):
    """
    Scans the network to find the PLC's IP address.
    """
    from ipaddress import ip_network
    import subprocess

    print("Scanning network for the PLC...")
    for ip in ip_network(target_ip_range).hosts():
        ip = str(ip)
        if ip == "192.168.9.24":  # Known PLC IP from the configuration
            print(f"Found PLC at IP: {ip}")
            return ip
        try:
            # Ping the IP to check if the device is active
            subprocess.check_output(["ping", "-c", "1", ip], timeout=1)
            print(f"Found PLC at IP: {ip}")
            return ip
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            print(f"Error scanning IP {ip}: {e}")
    print("PLC not found on the network.")
    return None

def restart_plc(plc_ip):
    """
    Sends a restart command to the PLC using Modbus TCP.
    """
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print("Failed to connect to the PLC.")
            return

        # Write to a specific register to trigger a restart
        # Note: This is an example and may need to be adjusted based on the PLC's Modbus map.
        restart_command = 0x0001  # Hypothetical Modbus register value for restart
        client.write_register(address=0, value=restart_command, unit=1)

        print("PLC restart command sent successfully.")
    except Exception as e:
        print(f"Error sending restart command: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Could not locate the PLC. Exiting.")
        exit(1)

    # Step 2: Send the restart command
    restart_plc(plc_ip)