import time
from scapy.all import sniff, IP

# Define the PLC's IP address (replace with your PLC's IP)
PLC_IP = "192.168.1.10"

# Threshold for detecting a potential DoS attack
REQUEST_THRESHOLD = 100  # Number of requests per second
TIME_WINDOW = 1  # Time window in seconds

# Counter for requests
request_count = 0
last_time = time.time()

def packet_callback(packet):
    global request_count, last_time

    if IP in packet and packet[IP].dst == PLC_IP:
        current_time = time.time()

        # Reset counter if the time window has passed
        if current_time - last_time > TIME_WINDOW:
            request_count = 0
            last_time = current_time

        # Increment request count
        request_count += 1

        # Alert if the threshold is exceeded
        if request_count > REQUEST_THRESHOLD:
            print(f"[ALERT] Potential DoS attack detected! Requests to {PLC_IP}: {request_count} in the last {TIME_WINDOW} second(s).")

# Start sniffing network traffic
print(f"Monitoring network traffic for potential DoS attacks targeting {PLC_IP}...")
sniff(prn=packet_callback, filter=f"dst host {PLC_IP}", store=False)