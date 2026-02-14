"""
Data Models

Data structures for sensor readings
"""

import json
from datetime import datetime


class SensorReading:
    """Represents a single sensor reading"""
    
    def __init__(self, temperature, humidity, air_quality, light_level):
        self.temperature = temperature
        self.humidity = humidity
        self.air_quality = air_quality
        self.light_level = light_level
        self.timestamp = datetime.utcnow().isoformat()
        self.device_id = "SmartEnviro-Gateway-01"  # Can be made configurable
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'device_id': self.device_id,
            'timestamp': self.timestamp,
            'temperature': round(self.temperature, 2),
            'humidity': round(self.humidity, 2),
            'air_quality': self.air_quality,
            'light_level': self.light_level
        }
    
    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    def __str__(self):
        return f"SensorReading(temp={self.temperature:.1f}°C, " \
               f"humidity={self.humidity:.1f}%, " \
               f"aq={self.air_quality}, light={self.light_level}lux)"
    
    def __repr__(self):
        return self.__str__()
