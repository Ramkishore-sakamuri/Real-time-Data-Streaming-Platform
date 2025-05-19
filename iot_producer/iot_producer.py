import json
import time
import random
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = 'localhost:29092' # Host accessible Kafka
RAW_DATA_TOPIC = 'iot-raw-data'

def create_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # For stronger delivery guarantees from producer
            retries=5,   # Retry sending on failure
            # enable_idempotence=True # For idempotent producer, ensures messages are written exactly once to a single partition
                                     # Requires broker version 0.11+ and acks='all'
        )
        logger.info("Kafka Producer created successfully.")
        return producer
    except KafkaError as e:
        logger.error(f"Error creating Kafka producer: {e}")
        return None

def generate_iot_data(device_id):
    return {
        "deviceId": device_id,
        "temperature": round(random.uniform(15.0, 40.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2),
        "timestamp": int(time.time() * 1000)
    }

if __name__ == "__main__":
    producer = create_producer()

    if not producer:
        logger.error("Exiting due to producer creation failure.")
        exit(1)

    device_ids = [f"sensor-{i}" for i in range(5)]

    try:
        while True:
            device_id = random.choice(device_ids)
            data = generate_iot_data(device_id)
            
            try:
                future = producer.send(RAW_DATA_TOPIC, key=data['deviceId'], value=data)
                # Block for 'successful' messages
                record_metadata = future.get(timeout=10)
                logger.info(f"Sent: {data} to topic {record_metadata.topic} partition {record_metadata.partition}")
            except KafkaError as e:
                logger.error(f"Error sending message: {e}")
                # Implement more robust error handling / retry logic if needed
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")


            time.sleep(random.uniform(0.5, 2.0)) # Simulate varied send rate
    except KeyboardInterrupt:
        logger.info("Producer shutting down...")
    finally:
        if producer:
            producer.flush()
            producer.close()
            logger.info("Producer closed.")
