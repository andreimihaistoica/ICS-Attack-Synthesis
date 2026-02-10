from pycomm3 import LogixDriver
import socket
import time

def discover_plc_ip(network_prefix="192.168.9"):
    """
    Discover the PLC's IP address on the local network.
    """
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)
                result = sock.connect_ex((ip, 44818))  # EtherNet/IP port
                if result == 0:
                    print(f"Found PLC at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    return None

def suppress_alarm(plc_ip):
    """
    Suppress the alarm by modifying the relevant PLC logic.
    """
    try:
        with LogixDriver(plc_ip) as plc:
            # Read current values of relevant tags
            m_actfan = plc.read("M_ACTFAN")
            q_fan = plc.read("Q_FAN")
            q_reda = plc.read("Q_REDA")
            q_greena = plc.read("Q_GREENA")

            print(f"Initial Values: M_ACTFAN={m_actfan}, Q_FAN={q_fan}, Q_REDA={q_reda}, Q_GREENA={q_greena}")

            # Suppress alarms by setting relevant tags to FALSE
            plc.write(("M_ACTFAN", False))  # Deactivate FanA
            plc.write(("Q_FAN", False))      # Turn off Fan output
            plc.write(("Q_REDA", False))     # Turn off Red LED
            plc.write(("Q_GREENA", False))    # Turn off Green LED

            # Verify changes
            m_actfan = plc.read("M_ACTFAN")
            q_fan = plc.read("Q_FAN")
            q_reda = plc.read("Q_REDA")
            q_greena = plc.read("Q_GREENA")

            print(f"Updated Values: M_ACTFAN={m_actfan}, Q_FAN={q_fan}, Q_REDA={q_reda}, Q_GREENA={q_greena}")

            print("Alarm suppression successful.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found on the network.")
        return

    # Step 2: Suppress the alarm
    suppress_alarm(plc_ip)

if __name__ == "__main__":
    main()