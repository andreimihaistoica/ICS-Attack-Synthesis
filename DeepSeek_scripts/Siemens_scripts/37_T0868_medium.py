import snap7
from snap7.util import get_operating_mode

def get_plc_ip_address():
    # This function is a placeholder for finding the PLC's IP address.
    # You can implement a network scan or use a predefined IP.
    # For simplicity, we'll return a hardcoded IP.
    return "192.168.0.1"

def detect_operating_mode(plc_ip):
    try:
        # Create a client instance
        client = snap7.client.Client()

        # Connect to the PLC
        client.connect(plc_ip, 0, 1)

        # Get the PLC status
        status = client.get_cpu_state()

        # Map the status to the operating mode
        operating_mode = get_operating_mode(status)

        # Disconnect from the PLC
        client.disconnect()

        return operating_mode

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    # Get the PLC's IP address
    plc_ip = get_plc_ip_address()
    print(f"PLC IP Address: {plc_ip}")

    # Detect the operating mode
    mode = detect_operating_mode(plc_ip)
    if mode is not None:
        print(f"PLC Operating Mode: {mode}")
    else:
        print("Failed to detect the operating mode.")

if __name__ == "__main__":
    main()