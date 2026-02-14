/*
 * Circular Buffer Implementation
 * 
 * Used for smoothing sensor data with a moving average
 */

#ifndef DATA_BUFFER_H
#define DATA_BUFFER_H

#include <Arduino.h>

class SensorBuffer {
private:
    float buffer[10];  // Fixed size buffer
    uint8_t index;     // Current write position
    uint8_t count;     // Number of valid entries
    
public:
    SensorBuffer();
    void add(float value);
    float getAverage();
    void clear();
    uint8_t getCount();
};

#endif // DATA_BUFFER_H
