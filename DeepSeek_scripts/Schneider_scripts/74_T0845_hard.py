from pycomm3 import LogixDriver
import socket

def find_plc_ip():
    # Scanning the network to find the PLC's IP address
    # This is a simple example and may need adjustments based on the network setup
    ip_range = "192.168.9."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 44818))  # EtherNet/IP port
                print(f"Found PLC at IP: {ip}")
                return ip
        except:
            continue
    print("PLC IP address not found.")
    return None

def upload_program(plc_ip):
    try:
        # Connect to the PLC using EtherNet/IP
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")
            
            # Attempt to upload the program
            program = plc.upload_program()
            if program:
                print("Program uploaded successfully.")
                # Save the program to a file
                with open("plc_program.txt", "w") as f:
                    f.write(program)
                print("Program saved to 'plc_program.txt'.")
            else:
                print("Failed to upload the program.")
    except Exception as e:
        print(f"Error uploading program: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        upload_program(plc_ip)
    else:
        print("Cannot proceed without the PLC's IP address.")