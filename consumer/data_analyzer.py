from confluent_kafka import Consumer, KafkaError
import json

# Kafka broker configuration
bootstrap_servers = 'localhost:9092'
group_id = 'transactional_data_analyzer_group'
topic = 'sensor_data_tx'

# Kafka Consumer configuration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest',
    'isolation.level': 'read_committed'  # Only read committed transactions
}

consumer = Consumer(consumer_config)
consumer.subscribe([topic])

if __name__ == '__main__':
    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('End of partition')
                else:
                    print(f'Error receiving message: {msg.error()}')
            else:
                print(f'Received (committed) message: {msg.value().decode("utf-8")}')
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()
