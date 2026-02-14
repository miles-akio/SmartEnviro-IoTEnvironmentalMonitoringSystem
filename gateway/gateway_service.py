#!/usr/bin/env python3
"""
SmartEnviro Gateway Service

Bridges BLE sensor nodes to AWS IoT Core via MQTT
Demonstrates: Python, BLE, MQTT, AWS IoT, data processing

Author: Miles Rodriguez
Created for Design Catapult interview demonstration
"""

import time
import signal
import sys
import logging
from ble_scanner import BLEScanner
from mqtt_publisher import MQTTPublisher
from config import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GatewayService:
    """Main gateway service orchestrating BLE and MQTT"""
    
    def __init__(self):
        self.ble_scanner = BLEScanner(BLE_DEVICE_NAME)
        self.mqtt_publisher = MQTTPublisher()
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the gateway service"""
        logger.info("=== SmartEnviro Gateway Starting ===")
        
        # Connect to MQTT
        if not self.mqtt_publisher.connect():
            logger.error("Failed to connect to AWS IoT - will retry")
        
        # Connect to BLE device
        if not self.ble_scanner.scan_and_connect():
            logger.error("Failed to connect to BLE device")
            return False
        
        if not self.ble_scanner.discover_characteristics():
            logger.error("Failed to discover characteristics")
            return False
        
        logger.info("=== Gateway Started Successfully ===")
        self.running = True
        
        # Main loop
        try:
            last_publish = time.time()
            
            while self.running:
                # Read sensors
                reading = self.ble_scanner.read_sensors()
                
                if reading:
                    # Publish if interval elapsed
                    if time.time() - last_publish >= PUBLISH_INTERVAL:
                        self.mqtt_publisher.publish(reading)
                        self.mqtt_publisher.flush_buffer()
                        last_publish = time.time()
                
                time.sleep(1)  # Read every second, publish every 5
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt - shutting down...")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the gateway service"""
        logger.info("Stopping gateway service...")
        self.running = False
        self.ble_scanner.disconnect()
        self.mqtt_publisher.disconnect()
        logger.info("=== Gateway Stopped ===")


def main():
    """Entry point"""
    gateway = GatewayService()
    gateway.start()


if __name__ == "__main__":
    main()
