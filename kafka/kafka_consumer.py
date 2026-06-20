import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "riskflow.transactions.raw",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    consumer_timeout_ms=10000,  # stop automatically after 10s of no new messages
)

print("Reading messages...")
count = 0
for message in consumer:
    print(message.value)
    count += 1
    if count >= 5:
        break

print(f"\nTotal messages read: {count}")