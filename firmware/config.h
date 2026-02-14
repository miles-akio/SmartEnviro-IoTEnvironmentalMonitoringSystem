/*
 * SmartEnviro Configuration File
 * 
 * All configuration constants and pin definitions
 */

#ifndef CONFIG_H
#define CONFIG_H

// ==================== DEVICE IDENTIFICATION ====================

#define DEVICE_NAME "SmartEnviro-Node-01"

// ==================== PIN DEFINITIONS ====================

// Sensor pins
#define DHT_PIN 4           // DHT22 data pin
#define DHT_TYPE DHT22      // DHT sensor type
#define MQ135_PIN 34        // MQ135 analog pin (ADC1_CH6)
#define LED_PIN 2           // Built-in LED

// I2C pins (default for ESP32, defined here for documentation)
#define I2C_SDA 21          // BH1750 SDA
#define I2C_SCL 22          // BH1750 SCL

// ==================== BLE UUIDs ====================

// Service UUID
#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"

// Characteristic UUIDs
#define TEMP_CHAR_UUID     "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define HUMIDITY_CHAR_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a9"
#define AQ_CHAR_UUID       "beb5483e-36e1-4688-b7f5-ea07361b26aa"
#define LIGHT_CHAR_UUID    "beb5483e-36e1-4688-b7f5-ea07361b26ab"

// ==================== TIMING CONFIGURATION ====================

// How often to read sensors (milliseconds)
#define SENSOR_READ_INTERVAL 5000   // 5 seconds

// How often to update BLE characteristics (milliseconds)
#define BLE_UPDATE_INTERVAL 1000    // 1 second

// ==================== DATA BUFFER CONFIGURATION ====================

// Size of circular buffer for smoothing
#define BUFFER_SIZE 10

// ==================== SENSOR CALIBRATION ====================

// DHT22 doesn't typically need calibration
// Add offsets here if your sensor is consistently off

#define TEMP_OFFSET 0.0      // Temperature offset in °C
#define HUMIDITY_OFFSET 0.0  // Humidity offset in %

// MQ135 calibration (if needed)
#define MQ135_RLOAD 10.0     // Load resistance in kOhms

#endif // CONFIG_H
