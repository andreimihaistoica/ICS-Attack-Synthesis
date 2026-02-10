import snap7
import socket
import subprocess

def find_plc_ip():
    # Define the subnet to scan
    subnet = "192.168.0.0/24"

    # Run the nmap command to scan the subnet
    command = f"nmap -sP {subnet}"
    output = subprocess.check_output(command, shell=True)

    # Parse the output to find the IP address of the PLC
    ip_address = None
    for line in output.decode("utf-8").splitlines():
        if "PLC" in line:
            ip_address = line.split()[-1]
            break

    return ip_address

def program_download(plc_ip):
    # Create a client object
    client = snap7.S7Client()

    # Connect to the PLC
    client.Connect(plc_ip, 0, 1)

    # Check if the connection is successful
    if client.Connected():
        print("Connected to the PLC")
    else:
        print("Failed to connect to the PLC")

    # Define the program to download
    program = """
    # This is a sample program
    M0.0 = 1
    M0.1 = 0
    """

    # Download the program to the PLC
    client.ProgramDownload(program)

    # Check if the download is successful
    if client.ProgramDownload(program):
        print("Program downloaded successfully")
    else:
        print("Failed to download program")

    # Disconnect from the PLC
    client.Disconnect()

def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC IP address: {plc_ip}")
    else:
        print("Failed to find PLC IP address")

    # Perform the program download
    if plc_ip:
        program_download(plc_ip)

if __name__ == "__main__":
    main()