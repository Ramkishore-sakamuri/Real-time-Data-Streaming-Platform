#!/bin/bash

# Define Kafka broker address within Docker network
KAFKA_INTERNAL_BROKER="kafka:9092"
# Wait for Kafka to be available (basic wait, can be improved)
echo "Waiting for Kafka to start..."
cub kafka-ready -b $KAFKA_INTERNAL_BROKER 1 60 # Uses confluentinc/cp-kafka-connect-base image tool

echo "Creating Kafka topics..."

# Raw IoT Data Topic
docker exec kafka kafka-topics --create \
  --bootstrap-server $KAFKA_INTERNAL_BROKER \
  --replication-factor 1 \
  --partitions 3 \
  --topic iot-raw-data \
  --if-not-exists

# Processed IoT Data Topic
docker exec kafka kafka-topics --create \
  --bootstrap-server $KAFKA_INTERNAL_BROKER \
  --replication-factor 1 \
  --partitions 3 \
  --topic iot-processed-data \
  --if-not-exists

echo "Kafka topics creation attempt finished."

docker exec kafka kafka-topics --list --bootstrap-server $KAFKA_INTERNAL_BROKER
