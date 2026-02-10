import pycomm3
import socket
import subprocess

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the engineering workstation
    # and the subnet is 192.168.1.0/24
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Ping the IP address to check if it's up
            response = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if response.returncode == 0:
                # Check if the IP is the PLC by attempting to connect
                with pycomm3.LogixDriver(ip) as plc:
                    if plc.info():
                        print(f"PLC found at IP: {ip}")
                        return ip
        except Exception as e:
            print(f"Error checking IP {ip}: {e}")
    print("PLC not found on the network.")
    return None

# Function to change the PLC's password
def change_plc_password(plc_ip, new_password):
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Assuming the current password is empty or known
            current_password = ""
            # Change the password
            plc.set_plc_password(current_password, new_password)
            print(f"PLC password changed to: {new_password}")
    except Exception as e:
        print(f"Error changing PLC password: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # New password to set
        new_password = "NewSecurePassword123"
        # Change the PLC's password
        change_plc_password(plc_ip, new_password)

if __name__ == "__main__":
    main()