import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = 'localhost:29092' # Host accessible Kafka
PROCESSED_DATA_TOPIC = 'iot-processed-data'
CONSUMER_GROUP_ID = 'results-viewer-group' # Different group ID

def create_consumer():
    try:
        consumer = KafkaConsumer(
            PROCESSED_DATA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest', # Start reading from the beginning of the topic
            group_id=CONSUMER_GROUP_ID,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            consumer_timeout_ms=1000 # Timeout to allow iteration
        )
        logger.info("Kafka Consumer created successfully.")
        return consumer
    except KafkaError as e:
        logger.error(f"Error creating Kafka consumer: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating consumer: {e}")
        return None


if __name__ == "__main__":
    consumer = create_consumer()

    if not consumer:
        logger.error("Exiting due to consumer creation failure.")
        exit(1)

    logger.info(f"Listening for messages on topic: {PROCESSED_DATA_TOPIC}")
    try:
        for message in consumer:
            logger.info(
                f"Received: Offset={message.offset}, Key={message.key}, Value={message.value}"
            )
    except KeyboardInterrupt:
        logger.info("Consumer shutting down...")
    except Exception as e:
        logger.error(f"An error occurred while consuming: {e}")
    finally:
        if consumer:
            consumer.close()
            logger.info("Consumer closed.")
