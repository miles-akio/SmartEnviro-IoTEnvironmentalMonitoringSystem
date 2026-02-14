"""
Gateway Configuration

All configuration constants for the gateway service
"""

# ==================== BLE CONFIGURATION ====================

BLE_DEVICE_NAME = "SmartEnviro-Node-01"

# Service and Characteristic UUIDs
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
TEMP_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
HUMIDITY_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a9"
AQ_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26aa"
LIGHT_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26ab"

# ==================== AWS IOT CONFIGURATION ====================

# IMPORTANT: Update these values with your AWS IoT settings
AWS_IOT_ENDPOINT = "your-endpoint.iot.us-east-1.amazonaws.com"
AWS_IOT_PORT = 8883

# Certificate paths (relative to gateway folder)
ROOT_CA_PATH = "./certs/root-CA.pem"
PRIVATE_KEY_PATH = "./certs/private.pem.key"
CERTIFICATE_PATH = "./certs/certificate.pem.crt"

# Client ID
CLIENT_ID = "SmartEnviro-Gateway-01"

# MQTT Topics
TOPIC_PUBLISH = "smartenviro/sensors/data"
TOPIC_SUBSCRIBE = "smartenviro/commands/#"

# ==================== BUFFER CONFIGURATION ====================

# Maximum number of readings to buffer when offline
MAX_BUFFER_SIZE = 100

# How often to publish data (seconds)
PUBLISH_INTERVAL = 5

# ==================== LOGGING CONFIGURATION ====================

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Log file (None for console only)
LOG_FILE = None
