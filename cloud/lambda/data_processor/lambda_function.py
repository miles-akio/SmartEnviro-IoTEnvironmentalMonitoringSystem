"""
SmartEnviro Data Processor Lambda Function

Processes incoming sensor data from AWS IoT and stores in DynamoDB
"""

import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Configuration
TABLE_NAME = 'SensorReadings'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789:SmartEnviroAlerts'

# Temperature threshold for alerts (Celsius)
TEMP_ALERT_THRESHOLD = 30.0


def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Triggered by AWS IoT Rule when data arrives on topic:
    smartenviro/sensors/data
    """
    try:
        # Parse incoming sensor data
        data = json.loads(event['body']) if 'body' in event else event
        
        print(f"Processing data from device: {data.get('device_id')}")
        
        # Prepare item for DynamoDB
        item = {
            'reading_id': str(uuid.uuid4()),
            'device_id': data['device_id'],
            'timestamp': data['timestamp'],
            'temperature': Decimal(str(data['temperature'])),
            'humidity': Decimal(str(data['humidity'])),
            'air_quality': data['air_quality'],
            'light_level': data['light_level'],
            'processed_at': datetime.utcnow().isoformat()
        }
        
        # Write to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=item)
        
        print(f"Stored reading {item['reading_id']} in DynamoDB")
        
        # Check for alert conditions
        check_alerts(item)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data processed successfully',
                'reading_id': item['reading_id']
            })
        }
    
    except KeyError as e:
        print(f"Missing required field: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Missing required field: {str(e)}')
        }
    
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }


def check_alerts(data):
    """Check sensor data for alert conditions"""
    alerts = []
    
    # Check temperature
    if float(data['temperature']) > TEMP_ALERT_THRESHOLD:
        alerts.append(f"High temperature detected: {data['temperature']}°C")
    
    # Check humidity (too low or too high)
    humidity = float(data['humidity'])
    if humidity < 20:
        alerts.append(f"Low humidity detected: {humidity}%")
    elif humidity > 80:
        alerts.append(f"High humidity detected: {humidity}%")
    
    # Send alerts if any
    if alerts:
        send_alert(data, alerts)


def send_alert(data, alerts):
    """Send SNS notification for alerts"""
    message = "SmartEnviro Alert\n\n"
    message += f"Device: {data['device_id']}\n"
    message += f"Time: {data['timestamp']}\n\n"
    message += "Alerts:\n"
    for alert in alerts:
        message += f"• {alert}\n"
    message += "\n"
    message += f"Current Readings:\n"
    message += f"Temperature: {data['temperature']}°C\n"
    message += f"Humidity: {data['humidity']}%\n"
    message += f"Air Quality: {data['air_quality']}\n"
    message += f"Light Level: {data['light_level']} lux\n"
    
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='SmartEnviro Alert',
            Message=message
        )
        print(f"Alert sent: {', '.join(alerts)}")
    except Exception as e:
        print(f"Failed to send alert: {str(e)}")
