/*
 * Circular Buffer Implementation
 */

#include "data_buffer.h"
#include "config.h"

SensorBuffer::SensorBuffer() : index(0), count(0) {
    memset(buffer, 0, sizeof(buffer));
}

void SensorBuffer::add(float value) {
    buffer[index] = value;
    index = (index + 1) % BUFFER_SIZE;  // Wrap around
    if (count < BUFFER_SIZE) {
        count++;
    }
}

float SensorBuffer::getAverage() {
    if (count == 0) {
        return 0.0f;
    }
    
    float sum = 0.0f;
    for (uint8_t i = 0; i < count; i++) {
        sum += buffer[i];
    }
    
    return sum / count;
}

void SensorBuffer::clear() {
    index = 0;
    count = 0;
    memset(buffer, 0, sizeof(buffer));
}

uint8_t SensorBuffer::getCount() {
    return count;
}
