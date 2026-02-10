import snap7
import socket
import re

# MITRE ATT&CK Technique: Collection - Point & Tag Identification (T0849)

# Configuration
PLC_IP = None # Will be discovered if None
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER_TEMPERATURE = 1  # Assuming FC1 and FC2 are in DB1
DB_NUMBER_FAN_CONTROL = 2 # Assuming FC1 and FC2 are in DB2
MOTOR_TEMP_OFFSET = 0  # Offset for Motor_Temp in DB_NUMBER_TEMPERATURE (bytes)
FAN_A_OFFSET = 0       # Offset for Activate_Fan_A in DB_NUMBER_FAN_CONTROL
FAN_B_OFFSET = 1       # Offset for Activate_Fan_B in DB_NUMBER_FAN_CONTROL
OVERHEATING_OFFSET = 2 #Offset for Overheating_Check
ACTIVATE_FAN_A_TAG = "Activate_Fan_A"
ACTIVATE_FAN_B_TAG = "Activate_Fan_B"
MOTOR_TEMP_TAG = "Motor_Temp"
OVERHEATING_CHECK_TAG = "Overheating_Check"

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This is a very basic approach and might not work in all environments.
    A more robust solution would involve using specialized PLC discovery tools.
    """
    try:
        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)  # Timeout after 2 seconds
        s.bind(('', 5005)) # Bind to any available address and port

        # Send a broadcast message (adjust subnet if needed)
        broadcast_address = '192.168.1.255' #Change this to the network that the PLC is on
        message = b'S7_PING'
        s.sendto(message, (broadcast_address, 5005))

        # Listen for a response
        data, addr = s.recvfrom(1024)
        print(f"Received {data!r} from {addr}")
        return addr[0]

    except socket.timeout:
        print("No PLC found within the timeout period.")
        return None
    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None
    finally:
        s.close()


def read_plc_data(plc_ip, rack, slot, db_number_temp, db_number_fan, temp_offset, fan_a_offset, fan_b_offset, overheating_offset):
    """
    Reads data from the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        db_number (int): The Data Block number.
        offset (int): The starting byte offset in the Data Block.
        length (int): The number of bytes to read.

    Returns:
        dict: A dictionary containing the collected data.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Read the data block
        db_temperature = plc.db_read(db_number_temp, temp_offset, 2) # Read 2 bytes for INT
        db_fan_control = plc.db_read(db_number_fan, fan_a_offset, 3)  # Read 3 bytes for bools

        #Extract Values
        motor_temp = snap7.util.get_int(db_temperature, 0)
        activate_fan_a = snap7.util.get_bool(db_fan_control, fan_a_offset-fan_a_offset, 0)
        activate_fan_b = snap7.util.get_bool(db_fan_control, fan_b_offset-fan_a_offset, 0)
        overheating_check = snap7.util.get_bool(db_fan_control, overheating_offset-fan_a_offset, 0)

        plc.disconnect()

        # Return the collected data with tags
        return {
            MOTOR_TEMP_TAG: motor_temp,
            ACTIVATE_FAN_A_TAG: activate_fan_a,
            ACTIVATE_FAN_B_TAG: activate_fan_b,
            OVERHEATING_CHECK_TAG: overheating_check
        }

    except Exception as e:
        print(f"Error reading PLC data: {e}")
        return None

def extract_tags_from_code(fc1_code, fc2_code, tags_table):
    """
    Extracts tags and their usage from the provided code blocks.
    This function identifies potential points of interest for an adversary.

    Args:
        fc1_code (str): The Structured Text code of FC1.
        fc2_code (str): The Structured Text code of FC2.
        tags_table (str): The tag table definition.

    Returns:
        dict: A dictionary containing identified tags and their descriptions.
    """

    tags = {}
    tag_lines = tags_table.strip().split('\n')

    for line in tag_lines:
        try:
            tag, data_type, address = line.split()
            tags[tag] = {"data_type": data_type, "address": address, "usage": []}
        except ValueError:
            print(f"Skipping malformed line: {line}")

    # Analyze FC1 code
    for tag in tags:
        if tag in fc1_code:
            tags[tag]["usage"].append("FC1")

    # Analyze FC2 code
    for tag in tags:
        if tag in fc2_code:
            tags[tag]["usage"].append("FC2")

    return tags

def main():
    global PLC_IP

    # Attempt to discover the PLC IP if not already defined
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP not found.  Please manually set PLC_IP.")
            return

    # Example FC1 and FC2 code (replace with your actual code)
    fc1_code = """
// Block FC1 - Motor Temperature Control
// Converted from LAD to SCL

// Network 1 - Reset Fan B if temperature < 300
IF "Motor_Temp" < 300 THEN
    RESET("Activate_Fan_B");
END_IF;

// Network 2 - Control Fan indicator lights
IF "Activate_Fan_A" THEN
    "Fan_A_Red" := TRUE;
END_IF;

IF "Activate_Fan_B" THEN
    "Fan_B_Red" := TRUE;
END_IF;

// Network 3 - Activate Fan A if temperature is between 260 and 400
IF IN_RANGE(INT#260, "Motor_Temp", INT#400) THEN
    SET("Activate_Fan_A");
END_IF;

// Network 4 - Activate Fan B if temperature > 320
IF "Motor_Temp" > 320 THEN
    SET("Activate_Fan_B");
    SET("Master_Fan_B_HMI");
    SET("Activate_Fan_B");
END_IF;

// Network 5 - Control Fan A outputs
IF "Activate_Fan_A" THEN
    "Fan_A" := TRUE;
    "Fan_A_Green" := TRUE;
END_IF;

// Network 6 - Control Fan B outputs
IF "Activate_Fan_B" THEN
    "Fan_B" := TRUE;
    "Fan_B_Green" := TRUE;
END_IF;
"""

    fc2_code = """
// Block FC2 - Fan Control with Timers
// Converted from LAD to SCL

// Network 1 - Fan A de-activate counter (~12 seconds)
"IEC_Counter_0_DB".CU := "Clock_0.5Hz";
IF "Fan_A" THEN
    "IEC_Counter_0_DB".R := FALSE;
ELSE
    "IEC_Counter_0_DB".R := TRUE;
END_IF;
"IEC_Counter_0_DB".PV := 15;
CTU("IEC_Counter_0_DB");

IF "IEC_Counter_0_DB".Q THEN
    "Tag_2" := TRUE;
    RESET("Activate_Fan_A");
END_IF;

// Network 2 - Fan A active timer (5 seconds)
// First Timer (TP)
"IEC_Timer_0_DB_1".IN := "Activate_Fan_A";
"IEC_Timer_0_DB_1".PT := T#30S;
TP("IEC_Timer_0_DB_1");

// Second Timer (TON)
"IEC_Timer_0_DB".IN := "Tag_2";
"IEC_Timer_0_DB".PT := T#30S;
TON("IEC_Timer_0_DB");

IF "IEC_Timer_0_DB_1".Q THEN
    "Fan_A" := TRUE;
    "Fan_A_Green" := TRUE;
END_IF;

IF "IEC_Timer_0_DB".Q THEN
    RESET("Activate_Fan_A");
END_IF;

// Network 3 - Fan B de-activate counter (~12 seconds)
IF "Motor_Temp" >= 300 THEN
    "IEC_Timer_0_DB_2".IN := "Tag_2";
    "IEC_Timer_0_DB_2".PT := T#3S;
    TP("IEC_Timer_0_DB_2");
    
    IF "IEC_Timer_0_DB_2".Q THEN
        RESET("Activate_Fan_B");
    END_IF;
END_IF;

// Network 4 - Fan B active timer (5 seconds)
// First Timer (TP)
"IEC_Timer_0_DB_3".IN := "Activate_Fan_B";
"IEC_Timer_0_DB_3".PT := T#30S;
TP("IEC_Timer_0_DB_3");

// Second Timer (TON)
"IEC_Timer_0_DB_4".IN := "Tag_2";
"IEC_Timer_0_DB_4".PT := T#30S;
TON("IEC_Timer_0_DB_4");

IF "IEC_Timer_0_DB_3".Q THEN
    "Fan_B" := TRUE;
    "Fan_B_Green" := TRUE;
END_IF;

IF "IEC_Timer_0_DB_4".Q THEN
    RESET("Activate_Fan_B");
END_IF;

// Network 5 - Overheating Check
IF "Motor_Temp" >= 300 THEN
    "Overheating_Check" := TRUE;
ELSE
    "Overheating_Check" := FALSE;
END_IF;

// Network 6 - Fan Status Indicators
IF "Fan_A" THEN
    "Fan_A_Red" := TRUE;
ELSE
    "Fan_A_Red" := FALSE;
END_IF;

IF "Fan_B" THEN
    "Fan_B_Red" := TRUE;
ELSE
    "Fan_B_Red" := FALSE;
END_IF;
"""

    tags_table = """Fan_A Bool %Q0.0
Fan_B Bool %Q0.1
Fan_A_Red Bool %Q0.4
Fan_A_Green Bool %Q0.5
Fan_B_Red Bool %Q0.2
Fan_B_Green Bool %Q0.3
System_Byte Byte %MB5
FirstScan Bool %M5.0
DiagStatusUpdate Bool %M5.1
AlwaysTRUE Bool %M5.2
AlwaysFALSE Bool %M5.3
Clock_Byte Byte %MB6
Clock_10Hz Bool %M6.0
Clock_5Hz Bool %M6.1
Clock_2.5Hz Bool %M6.2
Clock_2Hz Bool %M6.3
Clock_1.25Hz Bool %M6.4
Clock_1Hz Bool %M6.5
Clock_0.625Hz Bool %M6.6
Clock_0.5Hz Bool %M6.7
Motor_Temp Int %MW7
Activate_Fan_A Bool %M0.0
Activate_Fan_B Bool %M0.1
Master_Fan_B_HMI Bool %M0.5
Motor_Status Bool %M0.7
Master_OFF Bool %M0.6
Tag_1 Bool %M1.0
Overheating_Check Bool %M0.2
Tag_2 Bool %M0.4
Motor_Status_GET Bool %Q0.6
Tag_3 Bool %M8.0
Tag_4 Bool %M9.0
Tag_5 Bool %M10.0"""

    # Extract tags and their usage from the code
    extracted_tags = extract_tags_from_code(fc1_code, fc2_code, tags_table)

    # Read data from the PLC
    plc_data = read_plc_data(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER_TEMPERATURE, DB_NUMBER_FAN_CONTROL, MOTOR_TEMP_OFFSET, FAN_A_OFFSET, FAN_B_OFFSET, OVERHEATING_OFFSET)

    if plc_data:
        print("PLC Data:")
        for tag, value in plc_data.items():
            print(f"  {tag}: {value}")

        print("\nIdentified Tags and Usage:")
        for tag, info in extracted_tags.items():
            print(f"  Tag: {tag}, Data Type: {info['data_type']}, Address: {info['address']}, Used in: {', '.join(info['usage'])}")
    else:
        print("Failed to read PLC data.")

if __name__ == "__main__":
    main()