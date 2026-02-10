from pymodbus.client.sync import ModbusTcpClient
import socket
import time

def find_plc_ip(subnet="192.168.9.", start=1, end=254, port=502):
    """Scan the network to find the PLC's IP address."""
    for i in range(start, end + 1):
        ip = subnet + str(i)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                if s.connect_ex((ip, port)) == 0:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Error scanning IP {ip}: {e}")
    print("PLC not found on the network.")
    return None

def detect_operating_mode(ip_address):
    """Detect the operating mode of the PLC."""
    try:
        # Connect to the PLC
        client = ModbusTcpClient(ip_address)
        if not client.connect():
            print(f"Failed to connect to PLC at {ip_address}")
            return

        # Read the operating mode (example register, adjust as needed)
        # Schneider Electric PLCs may have specific registers for operating mode
        # This is a placeholder; you need to find the correct register for your PLC
        response = client.read_holding_registers(address=0x1000, count=1, unit=1)

        if response.isError():
            print("Error reading PLC operating mode.")
            return

        mode = response.registers[0]
        if mode == 0:
            print("PLC is in Run mode.")
        elif mode == 1:
            print("PLC is in Program mode.")
        elif mode == 2:
            print("PLC is in Remote mode.")
        elif mode == 3:
            print("PLC is in Stop mode.")
        elif mode == 4:
            print("PLC is in Reset mode.")
        elif mode == 5:
            print("PLC is in Test/Monitor mode.")
        else:
            print(f"Unknown operating mode: {mode}")

    except Exception as e:
        print(f"Error detecting operating mode: {e}")
    finally:
        client.close()

def main():
    # If the PLC's IP address is not known, scan the network to find it
    plc_ip = "192.168.9.24"  # Replace with the known IP or set to None to scan
    if not plc_ip:
        plc_ip = find_plc_ip()
        if not plc_ip:
            return

    # Detect the PLC's operating mode
    detect_operating_mode(plc_ip)

if __name__ == "__main__":
    main()