import socket
   import struct

   # Function to find the PLC's IP address
   def find_plc_ip():
       # Simulate a network scan to find the PLC
       # In a real scenario, you would use a network scanning tool like nmap
       return "192.168.1.100"

   # Function to send a command to the PLC
   def send_command(ip, command):
       # Simulate sending a command to the PLC
       # In a real scenario, you would use a protocol like Modbus or Ethernet/IP
       print(f"Sending command to PLC at {ip}: {command}")

   # Main function
   def main():
       # Find the PLC's IP address
       plc_ip = find_plc_ip()
       print(f"PLC IP address: {plc_ip}")

       # Simulate a benign action to change a variable
       # For example, changing the value of a variable that controls a fan
       command = "SET FanA_Off TRUE"
       send_command(plc_ip, command)

   if __name__ == "__main__":
       main()