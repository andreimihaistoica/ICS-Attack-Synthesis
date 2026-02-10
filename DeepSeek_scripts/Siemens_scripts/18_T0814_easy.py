import time
import socket
from collections import defaultdict
from datetime import datetime

# Configuration
PLC_IP = "192.168.1.10"  # Replace with your PLC's IP address
PLC_PORT = 502  # Modbus TCP port (common for PLCs)
THRESHOLD = 100  # Max allowed requests per second
LOG_FILE = "dos_detection.log"

# Track incoming requests
request_counter = defaultdict(int)

def log_event(message):
    """Log events to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def monitor_traffic():
    """Monitor incoming traffic to the PLC."""
    try:
        # Create a socket to listen for traffic
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", PLC_PORT))
        sock.listen(5)
        log_event(f"Started monitoring traffic to PLC at {PLC_IP}:{PLC_PORT}")

        while True:
            client_socket, client_address = sock.accept()
            ip = client_address[0]
            request_counter[ip] += 1

            # Check for DoS attempt
            if request_counter[ip] > THRESHOLD:
                log_event(f"Potential DoS attack detected from {ip}. Blocking IP.")
                block_ip(ip)

            client_socket.close()

            # Reset counter every second
            time.sleep(1)
            request_counter.clear()

    except Exception as e:
        log_event(f"Error: {e}")
    finally:
        sock.close()

def block_ip(ip):
    """Block the IP address using a firewall rule."""
    try:
        # Example: Use iptables to block the IP (Linux)
        import subprocess
        subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        log_event(f"Blocked IP: {ip}")
    except Exception as e:
        log_event(f"Failed to block IP {ip}: {e}")

if __name__ == "__main__":
    monitor_traffic()