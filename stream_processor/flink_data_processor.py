# This is a conceptual PyFlink job - requires a Flink cluster to run

from pyflink.datastream import StreamExecutionEnvironment, CheckpointConfig
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.common import WatermarkStrategy
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, DeliveryGuarantee
from pyflink.datastream.formats.json import JsonRowDeserializationSchema, JsonRowSerializationSchema
from pyflink.common.typeinfo import Types

# Define Kafka topic and brokers
kafka_topic = "sensor_data_tx"
kafka_brokers = "localhost:9092"
consumer_group = "flink-consumer-group"

# Define the schema for the sensor data
field_names = ["sensor_id", "timestamp", "temperature", "humidity"]
field_types = [Types.STRING(), Types.DOUBLE(), Types.DOUBLE(), Types.DOUBLE()]

# Create a StreamExecutionEnvironment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)  # For local testing

# Enable checkpointing for fault tolerance
checkpoint_config = env.get_checkpoint_config()
checkpoint_config.enable_externalized_checkpoints(
    CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION)
env.enable_checkpointing(5000)  # Checkpoint every 5 seconds

# Create a Kafka source with exactly-once semantics
json_deserialization_schema = JsonRowDeserializationSchema.builder() \
    .set_row_type(Types.ROW_NAMED(field_names, field_types)) \
    .build()

kafka_source = KafkaSource.builder() \
    .set_bootstrap_servers(kafka_brokers) \
    .set_topics(kafka_topic) \
    .set_group_id(consumer_group) \
    .set_starting_offsets(KafkaSource.EARLIEST_OFFSET()) \
    .set_value_only_deserializer(json_deserialization_schema) \
    .setProperty("isolation.level", "read_committed")  # Ensure exactly-once consumption
    .build()

# Create a data stream from the Kafka source
sensor_data_stream = env.from_source(
    kafka_source,
    WatermarkStrategy.no_watermarks(),
    "Kafka Source"
)

# Example: Simple processing - print the temperature
sensor_data_stream.map(lambda row: f"Temperature: {row.temperature}") \
    .print("Processed Temperature")

if __name__ == "__main__":
    env.execute("Flink IoT Data Processor")
