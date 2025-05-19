import time
import random
from confluent_kafka import Producer
from uuid import uuid4

# Kafka broker configuration
bootstrap_servers = 'localhost:9092'
topic = 'sensor_data_tx'
transactional_id = 'sensor-producer-' + str(uuid4())

# Kafka Producer configuration
producer_config = {
    'bootstrap.servers': bootstrap_servers,
    'transactional.id': transactional_id,
    'enable.idempotence': True  # Recommended for transactional producers
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
        producer.init_transactions()
        while True:
            producer.begin_transaction()
            try:
                for _ in range(random.randint(1, 3)):  # Send a small batch in each transaction
                    data = simulate_sensor_data()
                    print(f"Producing (in transaction): {data}")
                    producer.produce(topic, key=data['sensor_id'].encode('utf-8'), value=str(data).encode('utf-8'), callback=delivery_report)
                    producer.poll(0.05)
                producer.commit_transaction()
                time.sleep(1)
            except Exception as e:
                producer.abort_transaction()
                print(f"Error during transaction: {e}")
                time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.flush()
        producer.close()
