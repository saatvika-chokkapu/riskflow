import json
import time
import pandas as pd
from kafka import KafkaProducer

# Connect to the Kafka broker running in Docker
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: str(k).encode("utf-8"),
)

# Load the same merged dataset, sorted by simulated time so replay is chronological
transactions = pd.read_csv("data/raw/train_transaction.csv")
identity = pd.read_csv("data/raw/train_identity.csv")
merged = transactions.merge(identity, on="TransactionID", how="left")
merged = merged.sort_values("TransactionDT").reset_index(drop=True)

TOPIC_NAME = "riskflow.transactions.raw"
DELAY_SECONDS = 0.05  # ~20 messages/second — fast enough to see real throughput, slow enough to watch

print(f"Starting replay of {len(merged)} transactions...")

for i, row in merged.iterrows():
    message = {
        "txn_id": int(row["TransactionID"]),
        "card_id": str(row["card1"]),
        "amount": float(row["TransactionAmt"]),
        "product_cd": row["ProductCD"],
        "device_type": row["DeviceType"] if pd.notna(row["DeviceType"]) else None,
        "transaction_dt": int(row["TransactionDT"]),
        "is_fraud_label": int(row["isFraud"]),
    }

    producer.send(TOPIC_NAME, key=row["card1"], value=message)

    if i % 1000 == 0:
        print(f"Published {i} messages...")

    time.sleep(DELAY_SECONDS)

producer.flush()
print("Replay complete.")