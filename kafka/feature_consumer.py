import json
import boto3
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from kafka import KafkaConsumer

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("riskflow-card-velocity")

consumer = KafkaConsumer(
    "riskflow.transactions.raw",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

card_history = defaultdict(list)
REFERENCE_START = datetime(2017, 12, 1, tzinfo=timezone.utc)

print("Listening for transactions and computing velocity features...")

count = 0
with table.batch_writer(overwrite_by_pkeys=["card_id"]) as batch:
    for message in consumer:
        txn = message.value
        card_id = txn["card_id"]
        txn_time = REFERENCE_START + timedelta(seconds=txn["transaction_dt"])

        card_history[card_id].append(txn_time)
        cutoff_24h = txn_time - timedelta(hours=24)
        card_history[card_id] = [t for t in card_history[card_id] if t >= cutoff_24h]

        cutoff_1h = txn_time - timedelta(hours=1)
        txn_count_1h = sum(1 for t in card_history[card_id] if t >= cutoff_1h)
        txn_count_24h = len(card_history[card_id])

        batch.put_item(Item={
            "card_id": card_id,
            "txn_count_1h": txn_count_1h,
            "txn_count_24h": txn_count_24h,
            "last_txn_timestamp": txn_time.isoformat(),
        })

        count += 1
        if count % 1000 == 0:
            print(f"Processed {count} messages | unique cards tracked: {len(card_history)}")