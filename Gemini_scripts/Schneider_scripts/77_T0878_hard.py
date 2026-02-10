import snap7
import time

# Define PLC connection parameters
PLC_IP = '192.168.9.24'  # As given in the documentation
RACK = 0
SLOT = 1

# Define the memory addresses and data types from the PLC program
M_TOG_ADDRESS = 2  # %M2 - Toggle Off
Q_FAN_ADDRESS = 0  # %Q0.0 - Fan Output
Q_REDA_ADDRESS = 4  # %Q0.4 - Fan A Red LED
Q_GREENA_ADDRESS = 5 # %Q0.5 - Fan A Green LED

# Function to connect to the PLC
def connect_to_plc(ip, rack, slot):
    plc = snap7.client.Client()
    plc.connect(ip, rack, slot)
    return plc

# Function to inhibit the alarm by setting the M_TOG bit
def inhibit_alarm(plc):
    """
    Inhibits the fan alarm by setting the M_TOG bit to TRUE.
    This prevents the fan from turning on and the alarm from being triggered.
    """
    try:
        # Read the current value of the %M area (Memory Bits)
        mb_area = plc.read_area(snap7.const.areas['MK'], 0, 2, 1)  # Read 1 byte from M2 (M_TOG)
        #print(f"Current M Area: {mb_area}")

        # Modify the byte to set the M_TOG bit (M2) to 1.  Bytes are represented as integers so to represent the bit change need to use the correct bit representation for the binary number, or else it won't work correctly.
        # Create a byte array with the modified value
        modified_mb_area = bytearray(mb_area)
        modified_mb_area[0] |= (1 << 1)  # Set the second bit (M2) to 1
        
        # Write the modified byte back to the %M area
        plc.write_area(snap7.const.areas['MK'], 0, 2, modified_mb_area)  # Write to M2

        print("Alarm inhibition (M_TOG set to TRUE) attempted.")


    except Exception as e:
        print(f"Error inhibiting alarm: {e}")


# Function to restore normal operation by resetting the M_TOG bit
def restore_normal_operation(plc):
    """
    Restores normal operation by setting the M_TOG bit to FALSE.
    """
    try:
        # Read the current value of the %M area
        mb_area = plc.read_area(snap7.const.areas['MK'], 0, 2, 1)

        # Modify the byte to set the M_TOG bit (M2) to 0
        modified_mb_area = bytearray(mb_area)
        modified_mb_area[0] &= ~(1 << 1)  # Clear the second bit (M2) to 0

        # Write the modified byte back to the %M area
        plc.write_area(snap7.const.areas['MK'], 0, 2, modified_mb_area)

        print("Normal operation restored (M_TOG set to FALSE) attempted.")

    except Exception as e:
        print(f"Error restoring normal operation: {e}")

# Function to read the PLC outputs (for verification)
def read_plc_outputs(plc):
    """
    Reads the Q outputs and returns their values as a dictionary.
    """
    try:
        qb_area = plc.read_area(snap7.const.areas['PQ'], 0, 0, 1)  # Read 1 byte from Q0.0 to Q0.7
        # Extract individual output values from the byte.  This is how you correctly read bytes when using a single read for a range of outputs
        Q_FAN = (qb_area[0] >> 0) & 1  # Q0.0 - Right most bit
        Q_REDA = (qb_area[0] >> 4) & 1  # Q0.4
        Q_GREENA = (qb_area[0] >> 5) & 1 # Q0.5
        return {"Q_FAN": Q_FAN, "Q_REDA": Q_REDA, "Q_GREENA": Q_GREENA}
    except Exception as e:
        print(f"Error reading PLC outputs: {e}")
        return None

# Main execution block
if __name__ == "__main__":
    try:
        # 1. Connect to the PLC
        plc = connect_to_plc(PLC_IP, RACK, SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # 2. Inhibit the alarm (set M_TOG to TRUE)
        inhibit_alarm(plc)
        time.sleep(2)  # Give the PLC some time to process

        # 3. Verify the effect on the outputs
        outputs = read_plc_outputs(plc)
        if outputs:
            print("Outputs after alarm inhibition:")
            print(f"  Q_FAN: {outputs['Q_FAN']}")      #Fan Output
            print(f"  Q_REDA: {outputs['Q_REDA']}")    #Fan A Red LED
            print(f"  Q_GREENA: {outputs['Q_GREENA']}")  #Fan A Green LED

        # 4. Restore normal operation (set M_TOG to FALSE)
        restore_normal_operation(plc)
        time.sleep(2) # Give the PLC some time to process

        # 5. Verify the effect on the outputs after restoring
        outputs = read_plc_outputs(plc)
        if outputs:
            print("Outputs after restoring normal operation:")
            print(f"  Q_FAN: {outputs['Q_FAN']}")       #Fan Output
            print(f"  Q_REDA: {outputs['Q_REDA']}")     #Fan A Red LED
            print(f"  Q_GREENA: {outputs['Q_GREENA']}")   #Fan A Green LED


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.is_connected():
            plc.disconnect()
            print("Disconnected from PLC.")