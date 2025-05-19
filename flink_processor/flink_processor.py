from pyflink.common import Types, WatermarkStrategy, JsonRowDeserializationSchema, JsonRowSerializationSchema
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer, KafkaSink, KafkaSource
from pyflink.datastream.connectors.kafka import KafkaRecordSerializationSchema, KafkaOffsetsInitializer
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.descriptors import Schema, Kafka, Json
from pyflink.table.udf import udtf # For more complex transformations if needed
import json
import time

KAFKA_BROKERS_INTERNAL = "kafka:9092" # Internal Docker network address
RAW_DATA_TOPIC = "iot-raw-data"
PROCESSED_DATA_TOPIC = "iot-processed-data"
CONSUMER_GROUP_ID = "flink-iot-processor-group"

def run_flink_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    # Set TimeCharacteristic to EventTime if you plan to use event time semantics
    # env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
    
    # Checkpointing is configured in docker-compose.yml, but you can also set programmatically:
    # env.enable_checkpointing(10000) # milliseconds
    # env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
    # ... other checkpoint config

    # Define the type information for the Kafka JSON messages
    # This definition must match the JSON structure
    type_info = Types.ROW_NAMED(
        ["deviceId", "temperature", "humidity", "timestamp"],
        [Types.STRING(), Types.FLOAT(), Types.FLOAT(), Types.BIG_INT()]
    )

    # --- Kafka Source ---
    kafka_source = FlinkKafkaConsumer(
        topics=RAW_DATA_TOPIC,
        deserialization_schema=JsonRowDeserializationSchema.builder().type_info(type_info).build(),
        properties={
            'bootstrap.servers': KAFKA_BROKERS_INTERNAL,
            'group.id': CONSUMER_GROUP_ID,
            'auto.offset.reset': 'earliest' # Important for new consumer groups
        }
    ).set_commit_offsets_on_checkpoints(True) # Critical for exactly-once with Kafka source

    raw_data_stream = env.add_source(kafka_source, "KafkaRawDataSource")

    # --- Transformation ---
    def transform_data(row):
        device_id, temperature, humidity, original_timestamp = row
        status = "ALERT" if temperature > 30.0 else "NORMAL"
        processed_timestamp = int(time.time() * 1000)
        # Output as a dictionary to be serialized to JSON by KafkaSink's serializer
        return {
            "originalDeviceId": device_id,
            "readingTemperature": temperature,
            "readingHumidity": humidity,
            "originalTimestamp": original_timestamp,
            "processedTimestamp": processed_timestamp,
            "alertStatus": status
        }

    # Define output type for the map function if using DataStream API directly with complex types
    # For simple dicts going to JSON, this might not be strictly needed if serializer handles it.
    # However, being explicit is good.
    processed_type_info = Types.ROW_NAMED(
        ["originalDeviceId", "readingTemperature", "readingHumidity", 
         "originalTimestamp", "processedTimestamp", "alertStatus"],
        [Types.STRING(), Types.FLOAT(), Types.FLOAT(), 
         Types.BIG_INT(), Types.BIG_INT(), Types.STRING()]
    )
    # If using complex Pojo or Row types, ensure the output type is defined for the map function
    # For simplicity, we'll let the JSON serializer handle the dict.

    processed_stream = raw_data_stream.map(transform_data) # Output of map is Python dict here

    # --- Kafka Sink ---
    # For exactly-once sink, FlinkKafkaProducer with Semantic.EXACTLY_ONCE is the way.
    # It uses Kafka transactions. Kafka brokers must be version 0.11+
    # The Kafka cluster must also be configured to support transactions (see docker-compose.yml).
    
    # We need a serialization schema that takes our Python dict and makes a Kafka ProducerRecord
    # For PyFlink 1.17+, KafkaSink is the recommended new connector
    kafka_sink = KafkaSink.builder() \
        .set_bootstrap_servers(KAFKA_BROKERS_INTERNAL) \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
                .set_topic(PROCESSED_DATA_TOPIC)
                .set_value_serialization_schema(JsonRowSerializationSchema.builder()
                    # Define the structure of the output JSON
                    .with_type_info(Types.ROW_NAMED(
                        ["originalDeviceId", "readingTemperature", "readingHumidity", 
                         "originalTimestamp", "processedTimestamp", "alertStatus"],
                        [Types.STRING(), Types.FLOAT(), Types.FLOAT(), 
                         Types.BIG_INT(), Types.BIG_INT(), Types.STRING()]
                    ))
                    .build()
                )
                # If you want to set a key for the Kafka messages:
                # .set_key_serialization_schema(...) 
                .build()
        ) \
        .set_delivery_guarantee(DeliveryGuarantee.EXACTLY_ONCE) \
        .set_transactional_id_prefix("flink-iot-tx") # Unique prefix for transactions
        .build()

    # The KafkaSink expects DataStream<Row>, so we need to convert our dicts to Rows
    # if the JsonRowSerializationSchema doesn't implicitly handle dicts (it usually expects Flink Row types)
    # Let's ensure it's a Flink Row
    def dict_to_row(d):
        # Order must match the JsonRowSerializationSchema defined for the sink
        return Types.ROW(d["originalDeviceId"], d["readingTemperature"], d["readingHumidity"],
                         d["originalTimestamp"], d["processedTimestamp"], d["alertStatus"])

    # Define the RowType for the sink explicitly
    sink_row_type = Types.ROW_NAMED(
        ["originalDeviceId", "readingTemperature", "readingHumidity", 
         "originalTimestamp", "processedTimestamp", "alertStatus"],
        [Types.STRING(), Types.FLOAT(), Types.FLOAT(), 
         Types.BIG_INT(), Types.BIG_INT(), Types.STRING()]
    )

    processed_stream_as_rows = processed_stream.map(dict_to_row, output_type=sink_row_type)
    processed_stream_as_rows.sink_to(kafka_sink).name("KafkaProcessedDataSink")
    
    # Or for debugging, print to stdout (cannot guarantee exactly-once for print)
    # processed_stream.print().name("StdOutSink")

    env.execute("IoT Data Processing Job (Python)")

if __name__ == '__main__':
    # It's common to package the PyFlink job and submit it to the cluster.
    # This main guard is more for local testing or if you directly execute this script
    # in an environment where PyFlink is configured.
    # For Docker deployment, Flink will typically pick up the job from the mounted volume.
    print("Starting Flink job from Python script main...")
    run_flink_job()
    print("Flink job submission attempted from Python script main.")
