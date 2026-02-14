"""
BLE Scanner Module

Handles BLE device scanning, connection, and data reading
"""

import struct
import logging
from bluepy import btle
from data_models import SensorReading
from config import *

logger = logging.getLogger(__name__)


class BLEScanner:
    """Scans for and connects to BLE sensor nodes"""
    
    def __init__(self, device_name):
        self.device_name = device_name
        self.peripheral = None
        self.characteristics = {}
    
    def scan_and_connect(self, timeout=10, max_retries=3):
        """Scan for device and connect"""
        for attempt in range(max_retries):
            logger.info(f"Scanning for {self.device_name} (attempt {attempt + 1}/{max_retries})...")
            
            try:
                scanner = btle.Scanner()
                devices = scanner.scan(timeout)
                
                for dev in devices:
                    # Check device name in scan data
                    for (adtype, desc, value) in dev.getScanData():
                        if desc == "Complete Local Name" and value == self.device_name:
                            logger.info(f"Found device: {dev.addr}")
                            try:
                                self.peripheral = btle.Peripheral(dev.addr)
                                logger.info("Connected successfully")
                                return True
                            except Exception as e:
                                logger.error(f"Connection failed: {e}")
                                continue
                
                logger.warning(f"Device not found in scan (attempt {attempt + 1})")
                
            except Exception as e:
                logger.error(f"Scan error: {e}")
            
            if attempt < max_retries - 1:
                logger.info("Retrying in 5 seconds...")
                time.sleep(5)
        
        return False
    
    def discover_characteristics(self):
        """Discover and store BLE characteristics"""
        if not self.peripheral:
            logger.error("Not connected to peripheral")
            return False
        
        try:
            # Get all services
            services = self.peripheral.getServices()
            
            for service in services:
                if service.uuid.toString() == SERVICE_UUID:
                    logger.info("Found SmartEnviro service")
                    
                    # Get all characteristics
                    chars = service.getCharacteristics()
                    for char in chars:
                        uuid = char.uuid.toString()
                        self.characteristics[uuid] = char
                        logger.info(f"Found characteristic: {uuid}")
            
            return len(self.characteristics) > 0
        
        except Exception as e:
            logger.error(f"Characteristic discovery failed: {e}")
            return False
    
    def read_sensors(self):
        """Read all sensor values"""
        if not self.peripheral or not self.characteristics:
            logger.error("Cannot read sensors - not connected or no characteristics")
            return None
        
        try:
            # Read temperature (4 bytes, float)
            temp_char = self.characteristics.get(TEMP_CHAR_UUID)
            if not temp_char:
                logger.error("Temperature characteristic not found")
                return None
            
            temp_bytes = temp_char.read()
            temperature = struct.unpack('f', temp_bytes)[0]
            
            # Read humidity (4 bytes, float)
            humidity_char = self.characteristics.get(HUMIDITY_CHAR_UUID)
            humidity_bytes = humidity_char.read()
            humidity = struct.unpack('f', humidity_bytes)[0]
            
            # Read air quality (2 bytes, uint16)
            aq_char = self.characteristics.get(AQ_CHAR_UUID)
            aq_bytes = aq_char.read()
            air_quality = struct.unpack('H', aq_bytes)[0]
            
            # Read light level (2 bytes, uint16)
            light_char = self.characteristics.get(LIGHT_CHAR_UUID)
            light_bytes = light_char.read()
            light_level = struct.unpack('H', light_bytes)[0]
            
            return SensorReading(temperature, humidity, air_quality, light_level)
        
        except Exception as e:
            logger.error(f"Sensor read failed: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from device"""
        if self.peripheral:
            try:
                self.peripheral.disconnect()
                logger.info("Disconnected from BLE device")
            except Exception as e:
                logger.error(f"Disconnect error: {e}")
            finally:
                self.peripheral = None
                self.characteristics = {}
