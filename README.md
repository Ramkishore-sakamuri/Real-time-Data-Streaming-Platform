# Real-time IoT Data Streaming Platform

This project builds upon the basic framework to incorporate more advanced features for a real-time data streaming platform, including transactional producers and consumers for exactly-once delivery with Kafka, and outlines the integration of a stream processing framework like Apache Flink for fault-tolerant data analysis.

**Key Enhancements:**

* **Transactional Producers:** Demonstrates sending data to Kafka within a transaction.
* **Transactional Consumers:** Shows how to consume data from Kafka within a transaction to ensure exactly-once processing.
* **Flink Integration (Conceptual):** Includes a placeholder for a Flink job that would perform stateful, fault-tolerant stream processing.
* **Improved Error Handling:** Basic error handling in producer and consumer examples.

**Prerequisites:**

* Python 3.x
* Docker
* Docker Compose
* (For Flink) Java 8 or 11, and a Flink installation (not managed by this Docker Compose for simplicity).

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    cd realtime-data-platform
    ```

2.  **Start the Kafka environment using Docker Compose:**
    ```bash
    docker-compose up -d
    ```
    This will start a Zookeeper and a Kafka broker with transactional support enabled.

3.  **Install required Python libraries:**
    ```bash
    pip install confluent-kafka
    ```

## Running the Examples

1.  **Run the transactional data producer:**
    ```bash
    python producer/transactional_sensor_producer.py
    ```
    This script simulates IoT sensor data and sends it to the `sensor_data_tx` Kafka topic using transactions.

2.  **Run the transactional data consumer:**
    ```bash
    python consumer/transactional_data_consumer.py
    ```
    This script consumes data from the `sensor_data_tx` Kafka topic within a transaction.

3.  **Flink Data Processor (Conceptual):**
    The `stream_processor/flink_data_processor.py` file contains a conceptual outline of a Flink job. To run this, you would need a separate Flink cluster setup and package this Python code (using PyFlink) into a Flink application.

## Configuration

The `docker-compose.yml` now includes configurations to enable Kafka transactions.

## Fault Tolerance and Exactly-Once Delivery

* **Kafka Transactions:** The producer and consumer examples demonstrate the basic use of Kafka transactions to ensure that a batch of messages is either fully written or not at all, and that consumers read only committed transactional messages.
* **Flink:** Flink provides robust mechanisms for fault tolerance through checkpointing and state management. When integrated, Flink can process data from Kafka (potentially using transactional reads) and perform stateful computations with exactly-once guarantees.

## Further Development

* **Implement a full Flink job:** Develop the `flink_data_processor.py` into a runnable PyFlink application for complex stream processing.
* **Enhance Error Handling and Retry Mechanisms:** Implement more robust error handling, logging, and retry strategies in the producer and consumer.
* **Explore Kafka Partitioning and Replication:** Configure Kafka topics with appropriate partitioning and replication factors for scalability and fault tolerance.
* **Monitoring and Alerting:** Integrate tools for monitoring the health and performance of all components.
* **Consider a Schema Registry:** Use a schema registry (like Confluent Schema Registry) for managing data schemas and ensuring data consistency.
