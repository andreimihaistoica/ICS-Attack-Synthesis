from pycomm3 import LogixDriver
import socket
import sys

def find_plc_ip():
    # Replace with the expected PLC IP range or use a broadcast method
    # This is a basic example; more advanced methods can be used for network discovery
    plc_ip_range = '192.168.1.'
    for i in range(1, 255):
        ip = plc_ip_range + str(i)
        try:
            print(f"Scanning {ip}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 44818))  # 44818 is the default Allen-Bradley port
            if result == 0:
                print(f"PLC found at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    print("PLC not found in the specified range.")
    return None

def upload_program(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")
            
            # Upload the program logic
            program = plc.get_program('Prog1')  # Replace 'Prog1' with the actual program name
            if program:
                print("Program uploaded successfully:")
                print(program)
            else:
                print("Failed to upload the program.")
            
            # Optionally, upload the tag list
            tags = plc.get_tag_list()
            if tags:
                print("Tags uploaded successfully:")
                print(tags)
            else:
                print("Failed to upload tags.")
    except Exception as e:
        print(f"Error uploading program: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        upload_program(plc_ip)
    else:
        print("PLC IP address not found. Exiting...")
        sys.exit(1)