import requests
import hashlib

# Configuration
plc_ip = "192.168.1.100"
firmware_url = "http://example.com/firmware/latest.bin"
firmware_md5_url = "http://example.com/firmware/latest.md5"

# Function to download the firmware
def download_firmware(url):
    response = requests.get(url)
    if response.status_code == 200:
        with open("firmware.bin", "wb") as f:
            f.write(response.content)
        return True
    else:
        print("Failed to download firmware")
        return False

# Function to verify the firmware integrity
def verify_firmware(firmware_path, md5_url):
    response = requests.get(md5_url)
    if response.status_code == 200:
        expected_md5 = response.text.strip()
        with open(firmware_path, "rb") as f:
            firmware_data = f.read()
            actual_md5 = hashlib.md5(firmware_data).hexdigest()
        if actual_md5 == expected_md5:
            print("Firmware integrity verified")
            return True
        else:
            print("Firmware integrity check failed")
            return False
    else:
        print("Failed to download MD5 checksum")
        return False

# Function to update the firmware
def update_firmware(plc_ip, firmware_path):
    # This is a placeholder for the actual firmware update command
    # You need to replace this with the actual command or API call to update the firmware
    print(f"Updating firmware on PLC at {plc_ip} with {firmware_path}")
    # Example: os.system(f"scp {firmware_path} user@{plc_ip}:/path/to/firmware")
    # Example: os.system(f"ssh user@{plc_ip} 'command_to_update_firmware'")

# Main script
if download_firmware(firmware_url):
    if verify_firmware("firmware.bin", firmware_md5_url):
        update_firmware(plc_ip, "firmware.bin")
    else:
        print("Firmware update aborted due to integrity check failure")
else:
    print("Firmware update aborted due to download failure")