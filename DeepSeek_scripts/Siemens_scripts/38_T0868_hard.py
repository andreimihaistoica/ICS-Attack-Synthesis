import snap7
import snap7.client as c
from snap7.util import *
from snap7.types import *

def find_plc_ip():
    # This function scans the network to find the PLC's IP address.
    # You can use a network scanning tool or manually input the IP if known.
    # For simplicity, we assume the IP is known or manually input.
    plc_ip = "192.168.0.1"  # Replace with the actual IP or implement a scanner
    return plc_ip

def detect_operating_mode(plc_ip):
    # Create a PLC client object
    plc = c.Client()
    
    try:
        # Connect to the PLC
        plc.connect(plc_ip, 0, 1)
        
        # Read the operating mode from the PLC
        mode = plc.get_cpu_state()
        
        # Map the mode to human-readable strings
        mode_map = {
            S7CpuStatus.SYS_S_RUN: "Run",
            S7CpuStatus.SYS_S_STOP: "Stop",
            S7CpuStatus.SYS_S_DEBUG: "Debug",
            S7CpuStatus.SYS_S_RESET: "Reset",
            S7CpuStatus.SYS_S_PROGRAM: "Program"
        }
        
        # Get the mode string
        mode_str = mode_map.get(mode, "Unknown")
        
        print(f"PLC Operating Mode: {mode_str}")
        
    except Exception as e:
        print(f"Error detecting operating mode: {e}")
    finally:
        # Disconnect from the PLC
        plc.disconnect()

if __name__ == "__main__":
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    # Detect the operating mode
    detect_operating_mode(plc_ip)