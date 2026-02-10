import requests
import hashlib

# Function to get the firmware version from the PLC
def get_firmware_version(plc_ip):
    try:
        response = requests.get(f'http://{plc_ip}/firmware_version')
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error retrieving firmware version: {e}")
        return None

# Function to calculate the hash of the firmware
def calculate_firmware_hash(firmware_file_path):
    try:
        with open(firmware_file_path, 'rb') as file:
            firmware_data = file.read()
            firmware_hash = hashlib.sha256(firmware_data).hexdigest()
            return firmware_hash
    except FileNotFoundError:
        print("Firmware file not found.")
        return None

# Function to verify the firmware integrity
def verify_firmware_integrity(plc_ip, firmware_file_path, expected_hash):
    firmware_version = get_firmware_version(plc_ip)
    if firmware_version is None:
        return False

    print(f"Firmware version: {firmware_version}")

    firmware_hash = calculate_firmware_hash(firmware_file_path)
    if firmware_hash is None:
        return False

    print(f"Calculated firmware hash: {firmware_hash}")
    print(f"Expected firmware hash: {expected_hash}")

    return firmware_hash == expected_hash

# Main function
def main():
    plc_ip = '192.168.1.10'  # Replace with the actual PLC IP address
    firmware_file_path = 'path/to/firmware.bin'  # Replace with the path to the firmware file
    expected_hash = 'expected_sha256_hash'  # Replace with the expected SHA-256 hash

    if verify_firmware_integrity(plc_ip, firmware_file_path, expected_hash):
        print("Firmware integrity check passed.")
    else:
        print("Firmware integrity check failed. Potential tampering detected.")

if __name__ == "__main__":
    main()