#!/bin/bash

KAFKA_CONTAINER_NAME="kafka" # Using the explicit container name
KAFKA_INTERNAL_BOOTSTRAP_SERVER="${KAFKA_CONTAINER_NAME}:9092"

# Simple loop to wait for Kafka to be ready by checking if kafka-topics can list topics
echo "Waiting for Kafka to be ready..."
MAX_WAIT=60
COUNT=0
while [ $COUNT -lt $MAX_WAIT ]; do
    if docker exec "${KAFKA_CONTAINER_NAME}" kafka-topics --bootstrap-server "${KAFKA_INTERNAL_BOOTSTRAP_SERVER}" --list > /dev/null 2>&1; then
        echo "Kafka is ready."
        break
    fi
    echo -n "."
    sleep 5
    COUNT=$((COUNT + 5))
done

if [ $COUNT -ge $MAX_WAIT ]; then
    echo "Kafka did not become ready in ${MAX_WAIT} seconds. Exiting."
    exit 1
fi

echo "Creating Kafka topics..."

RAW_DATA_TOPIC='iot-raw-data'
PROCESSED_DATA_TOPIC='iot-processed-data'
REPLICATION_FACTOR=1 # For local dev; increase for production
PARTITIONS=3

# Create Raw IoT Data Topic
docker exec "${KAFKA_CONTAINER_NAME}" kafka-topics --create \
  --bootstrap-server "${KAFKA_INTERNAL_BOOTSTRAP_SERVER}" \
  --replication-factor "${REPLICATION_FACTOR}" \
  --partitions "${PARTITIONS}" \
  --topic "${RAW_DATA_TOPIC}" \
  --if-not-exists

# Create Processed IoT Data Topic
docker exec "${KAFKA_CONTAINER_NAME}" kafka-topics --create \
  --bootstrap-server "${KAFKA_INTERNAL_BOOTSTRAP_SERVER}" \
  --replication-factor "${REPLICATION_FACTOR}" \
  --partitions "${PARTITIONS}" \
  --topic "${PROCESSED_DATA_TOPIC}" \
  --if-not-exists

echo "Kafka topic creation script finished."
echo "Current topics:"
docker exec "${KAFKA_CONTAINER_NAME}" kafka-topics --list --bootstrap-server "${KAFKA_INTERNAL_BOOTSTRAP_SERVER}"
