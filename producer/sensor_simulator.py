import time
import random
from confluent_kafka import Producer

# Kafka broker configuration
bootstrap_servers = 'localhost:9092'
topic = 'sensor_data'

# Kafka Producer configuration
producer_config = {
    'bootstrap.servers': bootstrap_servers
}

producer = Producer(producer_config)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}')

def simulate_sensor_data():
    """Simulates IoT sensor data."""
    sensor_id = f'sensor-{random.randint(1, 10)}'
    timestamp = time.time()
    temperature = round(random.uniform(20.0, 30.0), 2)
    humidity = round(random.uniform(40.0, 60.0), 2)
    return {
        'sensor_id': sensor_id,
        'timestamp': timestamp,
        'temperature': temperature,
        'humidity': humidity
    }

if __name__ == '__main__':
    try:
        while True:
            data = simulate_sensor_data()
            print(f"Producing: {data}")
            producer.produce(topic, key=data['sensor_id'].encode('utf-8'), value=str(data).encode('utf-8'), callback=delivery_report)
            producer.poll(0.1)  # Serve delivery reports
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.flush()
