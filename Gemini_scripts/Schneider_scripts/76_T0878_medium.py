import snap7
import socket
import time

# Configuration - ADJUST THESE VALUES
PLC_IP = None  # Will be discovered if left as None
PLC_RACK = 0
PLC_SLOT = 1
ALARM_FLAG_ADDRESS = 'M100.0'  # Example:  Memory bit M100.0.  Change this to your alarm flag.
SUPPRESSION_DURATION = 60  # Duration (in seconds) to suppress the alarm.
ALARM_IO_ADDRESS = 'Q0.0' #Example: Output Q0.0, change it to your alarm I/O address

# Error Handling and Logging
def log_error(message):
    print(f"ERROR: {message}")
    # Consider adding more robust logging to a file

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the network.
    Requires nmap to be installed and accessible in the system's PATH.
    """
    try:
        import nmap  # Optional dependency, install with: pip install python-nmap

        nm = nmap.PortScanner()
        # Scan the local network (adjust the range if needed)
        nm.scan(hosts='192.168.1.0/24', arguments='-p 502')  # Modbus port 502 is a good indicator

        for host in nm.all_hosts():
            if 'vendor' in nm[host] and 'Schneider' in nm[host]['vendor'].values():
                print(f"Found Schneider PLC at IP: {host}")
                return host
        print("Schneider PLC not found on the network.")
        return None

    except ImportError:
        log_error("nmap module not found. Please install it: pip install python-nmap")
        return None
    except Exception as e:
        log_error(f"Error during IP discovery: {e}")
        return None


# Function to write to a PLC memory bit (flag)
def write_memory_bit(client, address, value):
    """Writes a boolean value (True/False) to a specific memory bit in the PLC."""
    try:
        area = snap7.util. Areas.MK
        byte_index = int(address[1:].split('.')[0])
        bit_index = int(address.split('.')[1])

        byte_array = client.read_area(area, 0, byte_index, 1)  # Read one byte
        snap7.util.set_bool(byte_array, 0, bit_index, value)  # Modify the bit
        client.write_area(area, 0, byte_index, byte_array)  # Write back the byte
        print(f"Successfully set {address} to {value}")
    except Exception as e:
        log_error(f"Error writing to memory bit {address}: {e}")

# Function to write to a PLC output (IO)
def write_output_bit(client, address, value):
    """Writes a boolean value (True/False) to a specific output bit in the PLC."""
    try:
        area = snap7.util. Areas.PQ
        byte_index = int(address[1:].split('.')[0])
        bit_index = int(address.split('.')[1])

        byte_array = client.read_area(area, 0, byte_index, 1)  # Read one byte
        snap7.util.set_bool(byte_array, 0, bit_index, value)  # Modify the bit
        client.write_area(area, 0, byte_index, byte_array)  # Write back the byte
        print(f"Successfully set {address} to {value}")
    except Exception as e:
        log_error(f"Error writing to output bit {address}: {e}")



def main():
    global PLC_IP  # Access the global variable

    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found.  Exiting.")
            return

    try:
        client = snap7.client.Client()
        client.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Suppress Alarm (Flag Method)
        print(f"Suppressing alarm flag {ALARM_FLAG_ADDRESS}...")
        write_memory_bit(client, ALARM_FLAG_ADDRESS, False) # Set to False to suppress (adjust as needed)

        #Suppress Alarm (IO method)
        print(f"Suppressing alarm IO {ALARM_IO_ADDRESS}...")
        write_output_bit(client, ALARM_IO_ADDRESS, False) # Set to False to suppress (adjust as needed)


        print(f"Alarm suppressed for {SUPPRESSION_DURATION} seconds.")
        time.sleep(SUPPRESSION_DURATION)

        # Restore Alarm (Flag Method) - REMOVE THIS LINE if you want the suppression to be permanent.
        print(f"Restoring alarm flag {ALARM_FLAG_ADDRESS}...")
        write_memory_bit(client, ALARM_FLAG_ADDRESS, True) # Restore to True (or whatever the original state was)

        # Restore Alarm (IO method) - REMOVE THIS LINE if you want the suppression to be permanent.
        print(f"Restoring alarm IO {ALARM_IO_ADDRESS}...")
        write_output_bit(client, ALARM_IO_ADDRESS, True) # Restore to True (or whatever the original state was)


        print("Alarm restored.")

    except snap7.exceptions.Snap7Exception as e:
        log_error(f"Snap7 Error: {e}")
    except Exception as e:
        log_error(f"General Error: {e}")
    finally:
        if 'client' in locals() and client.get_connected():  # Check if client is defined and connected
            client.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()