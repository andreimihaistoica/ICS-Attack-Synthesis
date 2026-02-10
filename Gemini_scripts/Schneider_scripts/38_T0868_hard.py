import snap7
import time
import socket

# Configuration
PLC_IP = "192.168.9.24"  # Replace with the PLC's IP address.  Script will attempt to find it if initial connect fails.
RACK = 0
SLOT = 1

# Function to dynamically find PLC IP (if initial connect fails)
def find_plc_ip():
    """Attempts to find the PLC's IP address by scanning the network.

    This is a simplified example and may not work in all network environments.
    It relies on basic pinging and assumes the PLC responds to ICMP.
    More robust discovery methods would involve specialized industrial protocols.
    """
    #This method will require network information. In this case 192.168.9.x where x is 1-254
    base_ip = "192.168.9."
    print("Attempting to discover PLC IP address...")
    for i in range(1, 255): # Check IPs 1 to 254
        ip = base_ip + str(i)
        try:
            socket.inet_aton(ip) # Check for invalid address
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1) # Set short timeout to avoid long delays
            result = s.connect_ex((ip, 102)) # Try connecting on port 102 (typical S7 port)
            if result == 0:
                print(f"Found PLC at IP address: {ip}")
                s.close()
                return ip
            s.close()
        except socket.error:
            pass
    print("PLC IP address not found on the network.")
    return None # PLC IP not found

# Function to read a memory bit (M area)
def read_memory_bit(plc, area, byte_address, bit_number):
    """Reads a single bit from the PLC's memory.

    Args:
        plc: The snap7 client object.
        area: The memory area ('M' for memory, 'I' for input, 'Q' for output).
        byte_address: The byte address of the memory location.
        bit_number: The bit number within the byte (0-7).

    Returns:
        True if the bit is set (1), False otherwise.  Returns None on error.
    """
    try:
        result = plc.read_area(area, 0, byte_address, 1)  # Read 1 byte
        byte_value = result[0]  # Get the byte value
        bit_value = (byte_value >> bit_number) & 1  # Extract the bit
        return bool(bit_value)
    except Exception as e:
        print(f"Error reading memory bit: {e}")
        return None

def main():
    """Main function to connect to the PLC and attempt to detect operating mode."""

    plc = snap7.client.Client()

    try:
        plc.connect(PLC_IP, RACK, SLOT)
        print(f"Connected to PLC at {PLC_IP}")
    except Exception as e:
        print(f"Error connecting to PLC at {PLC_IP}: {e}")

        #Attempt to discover the IP if initial connection fails
        discovered_ip = find_plc_ip()
        if discovered_ip:
             PLC_IP = discovered_ip # Update with the discovered IP
             try:
                 plc.connect(PLC_IP, RACK, SLOT)
                 print(f"Connected to PLC at {PLC_IP} (discovered IP)")
             except Exception as e:
                 print(f"Error connecting to PLC using discovered IP {PLC_IP}: {e}")
                 print("Failed to connect to PLC.  Exiting.")
                 return
        else:
            print("Failed to discover PLC IP.  Exiting.")
            return

    #Attempt to read the PLC mode register.  The location of the register varies
    #depending on the PLC model and configuration.  This is for the TM221.
    #A more robust solution would use the PLC's system functions to read the mode.
    #Mode is often encoded in a byte or word, but for simplicity, we will assume
    #it can be infered via memory bits.

    #Attempt to infer PLC operating mode based on known variables

    #Check if in Program Mode (inferred if Q_FAN is forced off)
    q_fan_forced_off = not read_memory_bit(plc, snap7.util.Areas.Q, 0, 0)
    if q_fan_forced_off:
        print("PLC Operating Mode: Possibly in Program Mode (Q_FAN is forced off).")
        plc.disconnect()
        return

    # Check Run mode based on output status (simplistic assumption).
    # Here we assume that if Q_FAN is active (True), PLC is running a program.

    q_fan_active = read_memory_bit(plc, snap7.util.Areas.Q, 0, 0) #Q0.0 is Q_FAN
    if q_fan_active is True:
        print("PLC Operating Mode: Likely in Run Mode (Q_FAN output active).")
    elif q_fan_active is False:
        print("PLC Operating Mode: Likely in Stop Mode (Q_FAN output inactive).")
    else:
        print("Could not determine PLC operating mode with this method.")
    plc.disconnect()

if __name__ == "__main__":
    main()