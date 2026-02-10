import snap7

def get_plc_ip():
    # Replace with your PLC's IP address or use a discovery method
    plc_ip = '192.168.0.1'  # Example IP address
    return plc_ip

def detect_operating_mode(plc_ip):
    try:
        # Create a client object
        client = snap7.S7Client()

        # Connect to the PLC
        client.ConnectTo(plc_ip, 0, 1)  # Rack 0, Slot 1

        # Get the CPU status
        cpu_status = client.GetCpuInfo()

        # Get the operating mode from the CPU status
        operating_mode = cpu_status['ModuleTypeName']

        # Print the operating mode
        print(f"Operating Mode: {operating_mode}")

        # Disconnect from the PLC
        client.Disconnect()

    except Exception as e:
        print(f"Error: {e}")

# Get the PLC's IP address
plc_ip = get_plc_ip()

# Detect the operating mode
detect_operating_mode(plc_ip)