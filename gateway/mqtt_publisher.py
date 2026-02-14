"""
MQTT Publisher Module

Handles publishing sensor data to AWS IoT Core
"""

import logging
from collections import deque
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from config import *

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Publishes sensor data to AWS IoT Core"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.publish_queue = deque(maxlen=MAX_BUFFER_SIZE)
    
    def connect(self, max_retries=3):
        """Connect to AWS IoT Core"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to AWS IoT Core (attempt {attempt + 1}/{max_retries})...")
                
                self.client = AWSIoTMQTTClient(CLIENT_ID)
                self.client.configureEndpoint(AWS_IOT_ENDPOINT, AWS_IOT_PORT)
                self.client.configureCredentials(
                    ROOT_CA_PATH,
                    PRIVATE_KEY_PATH,
                    CERTIFICATE_PATH
                )
                
                # Configure connection
                self.client.configureAutoReconnectBackoffTime(1, 32, 20)
                self.client.configureOfflinePublishQueueing(-1)
                self.client.configureDrainingFrequency(2)
                self.client.configureConnectDisconnectTimeout(10)
                self.client.configureMQTTOperationTimeout(5)
                
                # Connect
                if self.client.connect():
                    logger.info("Connected to AWS IoT Core")
                    self.connected = True
                    return True
                else:
                    logger.error("Failed to connect to AWS IoT Core")
            
            except Exception as e:
                logger.error(f"MQTT connection error: {e}")
            
            if attempt < max_retries - 1:
                logger.info("Retrying in 5 seconds...")
                time.sleep(5)
        
        return False
    
    def publish(self, reading):
        """Publish sensor reading to MQTT topic"""
        if not self.connected:
            # Buffer for later if offline
            self.publish_queue.append(reading)
            logger.warning(f"Offline - buffering data ({len(self.publish_queue)} readings)")
            return False
        
        try:
            # Publish reading
            self.client.publish(
                TOPIC_PUBLISH,
                reading.to_json(),
                1  # QoS level 1
            )
            logger.info(f"Published: Temp={reading.temperature:.1f}°C, "
                       f"Humidity={reading.humidity:.1f}%")
            return True
        
        except Exception as e:
            logger.error(f"Publish failed: {e}")
            self.publish_queue.append(reading)
            self.connected = False
            return False
    
    def flush_buffer(self):
        """Publish buffered readings"""
        if not self.connected or len(self.publish_queue) == 0:
            return
        
        logger.info(f"Flushing {len(self.publish_queue)} buffered readings")
        
        while self.publish_queue:
            reading = self.publish_queue.popleft()
            try:
                self.client.publish(
                    TOPIC_PUBLISH,
                    reading.to_json(),
                    1
                )
            except Exception as e:
                logger.error(f"Flush failed: {e}")
                # Put it back
                self.publish_queue.appendleft(reading)
                break
    
    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.client:
            try:
                self.client.disconnect()
                logger.info("Disconnected from AWS IoT Core")
            except Exception as e:
                logger.error(f"Disconnect error: {e}")
            finally:
                self.connected = False
