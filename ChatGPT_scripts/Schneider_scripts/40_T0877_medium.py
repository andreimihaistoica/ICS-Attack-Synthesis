import scapy.all as scapy
from pymodbus.client import ModbusTcpClient

# Step 1: Discover Schneider PLC's IP Address in the Network
def find_plc_ip():
    print("[+] Scanning network to detect PLC...")
    arp_request = scapy.ARP(pdst="192.168.1.1/24")   # Modify IP range as per your configuration
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for response in answered_list:
        if "Schneider" in response[1].hwsrc or "Modicon" in response[1].hwsrc:  # Identifying target device
            plc_ip = response[1].psrc
            print(f"[+] Schneider PLC detected at IP: {plc_ip}")
            return plc_ip

    print("[-] No PLC detected.")
    return None


# Step 2: Connect to PLC and Read I/O Image
def read_io_image(plc_ip):
    try:
        client = ModbusTcpClient(plc_ip, port=502)
        if not client.connect():
            print("[-] Failed to connect to PLC")
            return

        print("[+] Connected to PLC. Reading I/O Image...")

        # Read input image table (assumed to be at register 0, length 10)
        input_registers = client.read_discrete_inputs(0, 10)
        output_registers = client.read_coils(0, 10)

        if input_registers.isError() or output_registers.isError():
            print("[-] Error reading I/O image tables")
            return

        # Displaying results
        input_values = input_registers.bits
        output_values = output_registers.bits

        print(f"[+] Input Image: {input_values}")
        print(f"[+] Output Image: {output_values}")

        client.close()
    except Exception as e:
        print(f"[-] Error: {e}")

# Execute steps in sequence
plc_ip = find_plc_ip()
if plc_ip:
    read_io_image(plc_ip)