import snap7
import struct
import subprocess  # For finding IP address (if needed)

# Configuration (Adjust these values as needed)
PLC_IP = '192.168.9.114'  # Replace with the actual PLC IP address. Use subprocess if needed
PLC_RACK = 0
PLC_SLOT = 1
S7_PROGRAM = 1 # S7 Program Block to Stop before the program download

# Function to find PLC IP address (if needed)
def find_plc_ip():
    """
    Attempts to find the PLC's IP address using nmap (if available).
    This is a basic example and might need adjustments for your specific network.
    Requires nmap to be installed and in your system's PATH.
    """
    try:
        # Replace 'your_network_range' with the actual network range the PLC is on.
        # For example: '192.168.1.0/24'
        nmap_process = subprocess.run(['nmap', '-p', '102', '192.168.1.0/24'], capture_output=True, text=True)
        output = nmap_process.stdout
        
        # Parse nmap output to find the IP address.  This is a simplified example.
        for line in output.splitlines():
            if "Siemens" in line:
                ip_address = line.split()[4] # Get the IP adress from nmap
                return ip_address
        
        print("PLC IP not found using nmap.  Please specify the IP manually.")
        return None  # or raise an exception
    except FileNotFoundError:
        print("nmap is not installed. Please install it or specify the PLC IP manually.")
        return None
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None

# Function to set PLC mode to STOP
def set_plc_mode_stop(plc):
    """Sets the PLC to STOP mode."""
    try:
        # Stop program block
        plc.plc_stop()
        print("PLC set to STOP mode.")
    except Exception as e:
        print(f"Error setting PLC to STOP mode: {e}")

# Function to set PLC mode to RUN
def set_plc_mode_run(plc):
    """Sets the PLC to RUN mode."""
    try:
        plc.plc_start() # Try to start the PLC
        print("PLC set to RUN mode.")
    except Exception as e:
        print(f"Error setting PLC to RUN mode: {e}")
    

# Function to read PLC status
def read_plc_status(plc):
    """Reads the PLC status (RUN/STOP/ERROR)."""
    try:
        status = plc.get_cpu_state()
        print(f"PLC Status: {status}")
        return status
    except Exception as e:
        print(f"Error reading PLC status: {e}")
        return None

def main():
    global PLC_IP
    # If PLC_IP is not set, try to find it using nmap

    plc = snap7.client.Client()
    #plc.set_cpu_as_client()

    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Read initial PLC status
        read_plc_status(plc)

        # Set PLC to STOP mode
        set_plc_mode_stop(plc)

        # Optionally, verify the PLC is in STOP mode
        read_plc_status(plc)
        
        # Simulate some delay to potentially upload a program
        input("Press Enter to continue and set PLC back to RUN mode...")

        # Set PLC back to RUN mode
        set_plc_mode_run(plc)

        # Optionally, verify the PLC is in RUN mode
        read_plc_status(plc)
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

if __name__ == "__main__":
    main()