# Real-Time IoT Data Streaming Platform (Python)

This project demonstrates a real-time data streaming platform using Python, Apache Kafka, and Apache Flink, focusing on fault-tolerance and exactly-once delivery semantics.

**Components:**
- **IoT Producer (`iot_producer.py`):** Simulates IoT devices sending sensor data to Kafka.
- **Kafka:** Message broker for ingesting and distributing data.
- **Flink Processor (`flink_processor.py`):** PyFlink job that consumes raw data from Kafka, processes it, and writes results to another Kafka topic with exactly-once semantics.
- **Results Consumer (`results_consumer.py`):** Optional script to view the processed data from Kafka.
- **Docker Compose:** Manages Kafka, Zookeeper, and Flink services.

## Prerequisites
- Docker and Docker Compose installed.
- Python 3.8+ installed locally (for running producer/consumer scripts).
- `kafka-python` library for Python (install via `pip install -r requirements.txt`).
- PyFlink libraries (will be used by the Flink cluster, but having `apache-flink` in your local venv can be helpful for development: `pip install apache-flink`).

## Setup and Execution

1.  **Clone the repository (or create the files as described).**

2.  **Build and Start Docker Services:**
    Open a terminal in the project root and run:
    ```bash
    docker-compose up -d --build
    ```
    This will start Zookeeper, Kafka, Flink JobManager, and Flink TaskManager.
    You can view the Flink Web UI at `http://localhost:8081`.

3.  **Create Kafka Topics:**
    Open another terminal and run the topic creation script:
    ```bash
    # Make the script executable if needed: chmod +x kafka_helpers/create_topics.sh
    ./kafka_helpers/create_topics.sh
    ```
    *Note: This script uses `docker exec` to interact with the Kafka container. Ensure it runs after Kafka is fully up. The `cub kafka-ready` command in the script is a helper; if you don't have it or it causes issues, you might need to add a `sleep 30` before `docker exec kafka kafka-topics...` or use a more robust Kafka readiness check.*

4.  **Install Python Dependencies (for local producer/consumer):**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Submit the PyFlink Job:**
    The Flink job (`flink_processor.py`) is mounted into the Flink containers. You need to submit it to the running Flink cluster.
    
    Find the JobManager container ID:
    ```bash
    docker ps
    ```
    Then submit the job (replace `jobmanager_container_id` with the actual ID or name `jobmanager`):
    ```bash
    docker exec -it jobmanager /opt/flink/bin/flink run \
        -py /opt/flink/usrlib/flink_processor.py \
        -pym /opt/flink.usrlib.flink_processor # If flink_processor.py contains a main entry point
        # Or if your entry point is not a module:
        # -py /opt/flink/usrlib/flink_processor.py
        # Check PyFlink documentation for the most current submission syntax.
        # For PyFlink 1.17+, just specifying the python file is often enough if it has a `if __name__ == '__main__':` block.
    ```
    Alternatively, for simpler execution if your `flink_processor.py` is self-contained:
    ```bash
    docker exec -it jobmanager /opt/flink/bin/flink run -d -py /opt/flink/usrlib/flink_processor.py
    ```
    Monitor the Flink UI (`http://localhost:8081`) to see if the job is running. You might need to adjust paths or submission commands based on your exact PyFlink version and how it expects entry points. The `flink_processor.py` has a `if __name__ == '__main__'` which might be picked up by `flink run`.

6.  **Run the IoT Data Producer:**
    In a new terminal:
    ```bash
    python iot_producer/iot_producer.py
    ```

7.  **Run the Results Consumer (Optional):**
    In another new terminal:
    ```bash
    python results_consumer/results_consumer.py
    ```
    You should see the processed JSON messages printed to the console.

## Fault Tolerance & Exactly-Once Semantics
- **Kafka:**
    - Configured with replication factor 1 for this local setup (for production, use 3+).
    - Transactional features enabled for the broker.
- **Flink:**
    - Checkpointing is enabled and configured for `EXACTLY_ONCE` mode.
    - `FlinkKafkaConsumer` commits offsets to Kafka as part of Flink's checkpoints (`set_commit_offsets_on_checkpoints(True)`).
    - `KafkaSink` is configured with `DeliveryGuarantee.EXACTLY_ONCE`, which uses Kafka transactions to ensure atomic writes. This requires Kafka brokers version 0.11+ and a unique transactional ID prefix.

## Stopping the Platform
```bash
docker-compose down -v # -v removes volumes including any persisted checkpoint data
