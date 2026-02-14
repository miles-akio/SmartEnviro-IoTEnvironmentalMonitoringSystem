/*
 * SmartEnviro Sensor Node Firmware
 * Platform: ESP32
 * 
 * This is the main firmware file for the ESP32-based sensor node.
 * It reads environmental data from multiple sensors and transmits
 * via BLE to a gateway device.
 * 
 * Created for Design Catapult interview demonstration
 * Author: Miles Rodriguez
 */

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <DHT.h>
#include <Wire.h>
#include <BH1750.h>

#include "config.h"
#include "data_buffer.h"

// ==================== GLOBAL OBJECTS ====================

DHT dht(DHT_PIN, DHT_TYPE);
BH1750 lightMeter;

BLEServer* pServer = nullptr;
BLECharacteristic* pTempChar = nullptr;
BLECharacteristic* pHumidityChar = nullptr;
BLECharacteristic* pAQChar = nullptr;
BLECharacteristic* pLightChar = nullptr;

bool deviceConnected = false;
unsigned long lastSensorRead = 0;
unsigned long lastBLEUpdate = 0;

// ==================== SENSOR DATA STRUCTURE ====================

struct SensorData {
    float temperature;    // Celsius
    float humidity;       // Percentage
    uint16_t airQuality;  // ADC reading (0-4095)
    uint16_t lightLevel;  // Lux
    uint32_t timestamp;   // Milliseconds since boot
};

SensorData currentData = {0};

// Circular buffers for data smoothing
SensorBuffer tempBuffer;
SensorBuffer humidityBuffer;
SensorBuffer aqBuffer;
SensorBuffer lightBuffer;

// ==================== BLE CALLBACKS ====================

class ServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        Serial.println("BLE Client Connected");
        digitalWrite(LED_PIN, HIGH);  // LED on when connected
    }
    
    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        Serial.println("BLE Client Disconnected");
        digitalWrite(LED_PIN, LOW);
        
        // Restart advertising
        BLEDevice::startAdvertising();
        Serial.println("Advertising restarted");
    }
};

// ==================== SENSOR READING FUNCTIONS ====================

void readSensors() {
    // Read DHT22 (temperature & humidity)
    float temp = dht.readTemperature();
    float humid = dht.readHumidity();
    
    // Check if reads failed
    if (isnan(temp) || isnan(humid)) {
        Serial.println("DHT22 read failed!");
        return;
    }
    
    // Add to smoothing buffers
    tempBuffer.add(temp);
    humidityBuffer.add(humid);
    
    // Read MQ135 air quality sensor (analog)
    uint16_t aqRaw = analogRead(MQ135_PIN);
    aqBuffer.add(aqRaw);
    
    // Read BH1750 light sensor (I2C)
    uint16_t lux = lightMeter.readLightLevel();
    lightBuffer.add(lux);
    
    // Update current data with smoothed values
    currentData.temperature = tempBuffer.getAverage();
    currentData.humidity = humidityBuffer.getAverage();
    currentData.airQuality = (uint16_t)aqBuffer.getAverage();
    currentData.lightLevel = (uint16_t)lightBuffer.getAverage();
    currentData.timestamp = millis();
    
    // Debug output
    Serial.printf("Temp: %.2f°C | Humidity: %.2f%% | AQ: %d | Light: %d lux\n",
                  currentData.temperature, currentData.humidity, 
                  currentData.airQuality, currentData.lightLevel);
}

// ==================== BLE UPDATE FUNCTIONS ====================

void updateBLECharacteristics() {
    if (!deviceConnected) return;
    
    // Convert float to bytes for BLE transmission
    uint8_t tempBytes[4];
    memcpy(tempBytes, &currentData.temperature, sizeof(float));
    pTempChar->setValue(tempBytes, 4);
    pTempChar->notify();
    
    uint8_t humidityBytes[4];
    memcpy(humidityBytes, &currentData.humidity, sizeof(float));
    pHumidityChar->setValue(humidityBytes, 4);
    pHumidityChar->notify();
    
    // Send uint16 values directly
    pAQChar->setValue(currentData.airQuality);
    pAQChar->notify();
    
    pLightChar->setValue(currentData.lightLevel);
    pLightChar->notify();
}

// ==================== SETUP ====================

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== SmartEnviro Sensor Node Starting ===");
    
    // Initialize LED
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    // Initialize sensors
    dht.begin();
    Wire.begin();
    
    if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
        Serial.println("BH1750 initialized");
    } else {
        Serial.println("BH1750 initialization failed!");
    }
    
    // Initialize BLE
    BLEDevice::init(DEVICE_NAME);
    
    // Create BLE Server
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());
    
    // Create BLE Service
    BLEService *pService = pServer->createService(SERVICE_UUID);
    
    // Create BLE Characteristics
    pTempChar = pService->createCharacteristic(
        TEMP_CHAR_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    pTempChar->addDescriptor(new BLE2902());
    
    pHumidityChar = pService->createCharacteristic(
        HUMIDITY_CHAR_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    pHumidityChar->addDescriptor(new BLE2902());
    
    pAQChar = pService->createCharacteristic(
        AQ_CHAR_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    pAQChar->addDescriptor(new BLE2902());
    
    pLightChar = pService->createCharacteristic(
        LIGHT_CHAR_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    pLightChar->addDescriptor(new BLE2902());
    
    // Start service
    pService->start();
    
    // Start advertising
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();
    
    Serial.println("BLE advertising started");
    Serial.println("=== Setup Complete ===\n");
}

// ==================== MAIN LOOP ====================

void loop() {
    unsigned long currentMillis = millis();
    
    // Read sensors at defined interval
    if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
        readSensors();
        lastSensorRead = currentMillis;
    }
    
    // Update BLE characteristics at defined interval
    if (currentMillis - lastBLEUpdate >= BLE_UPDATE_INTERVAL) {
        updateBLECharacteristics();
        lastBLEUpdate = currentMillis;
    }
    
    // Blink LED when not connected (heartbeat)
    if (!deviceConnected) {
        static unsigned long lastBlink = 0;
        if (currentMillis - lastBlink >= 1000) {
            digitalWrite(LED_PIN, !digitalRead(LED_PIN));
            lastBlink = currentMillis;
        }
    }
    
    delay(10);  // Small delay to prevent watchdog timer issues
}
