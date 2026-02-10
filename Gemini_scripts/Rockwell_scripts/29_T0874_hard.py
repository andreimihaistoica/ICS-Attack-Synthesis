import sys
import time
import struct
import socket
import threading
from ctypes import *

# MITRE ATT&CK Technique T1622: Hooking
# Implements IAT Hooking against a simulated PLC-communicating process.

# ========================= Simulated PLC Communication (Replace with actual PLC interaction) =========================
PLC_IP = "127.0.0.1"  # Default, will attempt to auto-detect
PLC_PORT = 502  # Example Modbus port, adjust as needed

class PLCComm:  # Simulate reading/writing PLC data
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = None
        self.connected = False
        self.data = { # Simulate PLC Tag data
            "NewVariable": False,
            "Activate_FanA": False,
            "FanA_Timer": 0.0, # float
            "START": True,
            "STOP": False,
            "TON_1.Q": False,
            "FanA_Off": False,
            "Tog_Off": False,
        } # In real code, replace with actual PLC comm library.

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print(f"Connected to PLC at {self.ip}:{self.port}")
        except Exception as e:
            print(f"Error connecting to PLC: {e}")
            self.connected = False

    def disconnect(self):
        if self.connected and self.sock:
            self.sock.close()
            self.connected = False
            print("Disconnected from PLC.")

    def read_tag(self, tag_name):
        if self.connected:
            # Simulate reading a tag value from the PLC
            if tag_name in self.data:
                return self.data[tag_name]
            else:
                print(f"Tag '{tag_name}' not found.")
                return None
        else:
            print("Not connected to PLC.  Attempting to reconnect...")
            self.connect()
            if self.connected:
                return self.read_tag(tag_name)
            else:
                print("Failed to connect.")
                return None


    def write_tag(self, tag_name, value):
        if self.connected:
            # Simulate writing a tag value to the PLC
            if tag_name in self.data:
                self.data[tag_name] = value
                print(f"Wrote {value} to tag '{tag_name}'")
            else:
                print(f"Tag '{tag_name}' not found.")
        else:
            print("Not connected to PLC. Attempting to reconnect...")
            self.connect()
            if self.connected:
                self.write_tag(tag_name, value)
            else:
                print("Failed to connect.")


def find_plc_ip():
    """
    Simulates a network scan to find the PLC IP.  REPLACE THIS WITH A REAL DISCOVERY MECHANISM!
    In a real attack, this might be done passively or actively.
    """
    # This is a placeholder. In reality, you would use network scanning tools
    # (e.g., nmap, scapy) or protocols like ARP to discover the PLC's IP.
    print("Simulating PLC IP discovery...")
    # Simulate finding the PLC IP (replace with actual discovery code)
    # Example (dangerous, just for illustration, don't do this in production!):
    # Replace with code that scans a known range and identifies the PLC (e.g., based on Modbus responses)
    return "192.168.1.100"  # Hardcoded IP address

# ========================= IAT Hooking Simulation =========================

# This is a simplified simulation of IAT hooking.  It does NOT actually modify
# the IAT of the PLC communication process.  That would require elevated privileges
# and is beyond the scope of this example.  Instead, it demonstrates the *concept*
# of how an attacker might redirect API calls.

original_read_tag = None  # Store the original function
hook_active = False  # Global flag to control the hook

def hooked_read_tag(plc_comm, tag_name):
    """
    This is the hooked version of the read_tag function.
    It intercepts the call and can modify the behavior.
    """
    global hook_active
    if hook_active:
        print("[Hooked!] read_tag intercepted for tag:", tag_name)
        if tag_name == "Activate_FanA":
            print("[Hooked!]  Returning forced value (TRUE)")
            return True  # Force Activate_FanA to always be TRUE
        elif tag_name == "START":
            print("[Hooked!]  Returning forced value (FALSE)")
            return False # Force START to be always False
        else:
            print("[Hooked!]  Calling original function...")
            return original_read_tag(plc_comm, tag_name)  # Call the original function

    else:
        return original_read_tag(plc_comm, tag_name) # Call the original if hook inactive

def install_hook(plc_comm_object):
    """
    Simulates installing the IAT hook.  In reality, this would involve
    modifying the IAT of the target process. This version only redirects the call.
    """
    global original_read_tag, hook_active
    original_read_tag = plc_comm_object.read_tag  # Save the original function
    plc_comm_object.read_tag = hooked_read_tag  # Replace with the hooked function
    hook_active = True
    print("IAT Hook installed.")

def remove_hook(plc_comm_object):
    """
    Simulates removing the IAT hook.
    """
    global original_read_tag, hook_active
    if original_read_tag:
        plc_comm_object.read_tag = original_read_tag  # Restore the original function
        original_read_tag = None
        hook_active = False
        print("IAT Hook removed.")
    else:
        print("No hook to remove.")

def plc_control_loop(plc_comm_object):
  """
  Simulates a control loop reading and writing data.
  """
  try:
    while True:
      # Read PLC tags (these calls could be hooked!)
      start_state = plc_comm_object.read_tag("START")
      activate_fan_a = plc_comm_object.read_tag("Activate_FanA")
      fan_a_off = plc_comm_object.read_tag("FanA_Off")

      print(f"Read from PLC: START={start_state}, Activate_FanA={activate_fan_a}, FanA_Off={fan_a_off}")

      # Simulate logic based on PLC data
      # This section mimics the ladder logic from the prompt
      if activate_fan_a:
          print("Fan is supposed to be active.")
      else:
          print("Fan is supposed to be inactive.")

      if start_state and not fan_a_off:
          print("Starting some process.")

      #Write to PLC (simulated)
      plc_comm_object.write_tag("NewVariable", not activate_fan_a)

      time.sleep(2)  # Simulate a control loop cycle
  except KeyboardInterrupt:
    print("Exiting control loop.")

if __name__ == "__main__":
    # 1. Discover PLC IP (replace with real discovery)
    # PLC_IP = find_plc_ip() # Commented out so it doesn't override 127.0.0.1 for testing purposes.
    print(f"Using PLC IP: {PLC_IP}")

    # 2. Initialize PLC communication
    plc_comm = PLCComm(PLC_IP, PLC_PORT)
    plc_comm.connect()

    if not plc_comm.connected:
        print("Failed to connect to PLC. Exiting.")
        sys.exit(1)

    # 3. Install the hook
    install_hook(plc_comm)

    # 4. Run the PLC control loop (which now uses the hooked function)
    control_thread = threading.Thread(target=plc_control_loop, args=(plc_comm,))
    control_thread.daemon = True # Allow main thread to exit even if this is running.
    control_thread.start()

    input("Press Enter to remove the hook and exit...\n")

    # 5. Remove the hook
    remove_hook(plc_comm)

    plc_comm.disconnect()
    print("Script finished.")