from snap7 import client
import socket

def find_plc_ip():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 0))
    sock.settimeout(1)

    # Send a broadcast message to the network
    message = b"Hello, PLC!"
    sock.sendto(message, ("255.255.255.255", 102))

    # Listen for responses
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        return None

def upload_program(plc_ip, local_file_path):
    # Create a client object
    plc = client.Client()
    
    # Try to connect to the PLC
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        return
    
    # Upload the program from the PLC to the local machine
    try:
        # The `upload` method is not directly available in snap7 for uploading programs.
        # Instead, you can read blocks from the PLC. The following example reads a DB (Data Block).
        # You need to adjust this based on the type of block and the specifics of your program.
        db_number = 1  # Replace with the number of the DB you want to read
        db_data = plc.read_area(0x84, db_number, 0, 100)  # Read 100 bytes from DB1
        
        # Save the data to a local file
        with open(local_file_path, 'wb') as file:
            file.write(db_data)
        
        print("Program uploaded successfully.")
    except Exception as e:
        print(f"Failed to upload program: {e}")
    finally:
        # Always disconnect when you're done
        plc.disconnect()

def main():
    local_file_path = "path/to/save/program.s7p"
    
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP address: {plc_ip}")
        upload_program(plc_ip, local_file_path)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()