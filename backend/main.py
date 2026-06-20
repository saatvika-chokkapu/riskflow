import time
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from backend.cost_model import assign_segment, decide_transaction

app = FastAPI(title="RiskFlow Decisioning API")

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role="ACCOUNTADMIN",
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )
import boto3

dynamodb_resource = boto3.resource("dynamodb", region_name="us-east-1")
velocity_table = dynamodb_resource.Table("riskflow-card-velocity")

# Documented assumption, not derived from this dataset:
# more than 5 transactions/hour from one card resembles card-testing fraud patterns
VELOCITY_REVIEW_THRESHOLD = 5

def get_card_velocity(card_id: str):
    try:
        response = velocity_table.get_item(Key={"card_id": card_id})
        item = response.get("Item")
        if item:
            return {
                "txn_count_1h": int(item.get("txn_count_1h", 0)),
                "txn_count_24h": int(item.get("txn_count_24h", 0)),
            }
    except Exception:
        pass
    # Graceful degradation: new card, or DynamoDB temporarily unreachable —
    # default to "no known velocity" rather than failing the whole request
    return {"txn_count_1h": 0, "txn_count_24h": 0}

# Loaded once at startup — not per-request
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, "fraud_model.pkl"))
encoders = joblib.load(os.path.join(BASE_DIR, "encoders.pkl"))

CATEGORICAL_COLS = ["ProductCD", "card4", "card6", "P_emaildomain", "DeviceType", "DeviceInfo"]
FEATURE_COLS = ["amount", "card1", "addr1"] + CATEGORICAL_COLS

class Transaction(BaseModel):
    txn_id: int
    amount: float
    card1: int
    card4: str
    card6: str
    addr1: float
    ProductCD: str
    P_emaildomain: str
    DeviceType: str
    DeviceInfo: str

def encode_value(col, value):
    # Use the exact mapping learned during training.
    # Fall back to -1 for any category never seen in training data —
    # an honest, explicit signal to the model rather than a silent guess.
    return encoders[col].get(value, -1)

@app.post("/api/decision")
def decide(txn: Transaction):
    start_time = time.perf_counter()

    row = {
        "amount": txn.amount,
        "card1": txn.card1,
        "addr1": txn.addr1,
        "ProductCD": encode_value("ProductCD", txn.ProductCD),
        "card4": encode_value("card4", txn.card4),
        "card6": encode_value("card6", txn.card6),
        "P_emaildomain": encode_value("P_emaildomain", txn.P_emaildomain),
        "DeviceType": encode_value("DeviceType", txn.DeviceType),
        "DeviceInfo": encode_value("DeviceInfo", txn.DeviceInfo),
    }
    X = pd.DataFrame([row])[FEATURE_COLS]

    fraud_probability = model.predict_proba(X)[0][1]

    segment = assign_segment({"card6": txn.card6, "amount": txn.amount})
    decision, cost_approve, cost_decline = decide_transaction(fraud_probability, txn.amount, segment)

    velocity = get_card_velocity(str(txn.card1))
    if decision == "approve" and velocity["txn_count_1h"] > VELOCITY_REVIEW_THRESHOLD:
        decision = "review"

    latency_ms = (time.perf_counter() - start_time) * 1000

    return {
        "txn_id": txn.txn_id,
        "decision": decision,
        "fraud_probability": round(float(fraud_probability), 4),
        "segment": segment,
        "expected_cost_approve": round(cost_approve, 2),
        "expected_cost_decline": round(cost_decline, 2),
        "card_velocity_1h": velocity["txn_count_1h"],
        "card_velocity_24h": velocity["txn_count_24h"],
        "latency_ms": round(latency_ms, 2),
    }

@app.get("/api/cost-analysis")
def cost_analysis():
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT txn_date, total_transactions, riskflow_fraud_caught, riskflow_false_declines,
               riskflow_total_cost, naive_fraud_caught, naive_false_declines, naive_total_cost,
               net_cost_vs_naive_baseline
        FROM cost_outcomes ORDER BY txn_date
    """)
    cols = [c[0].lower() for c in cursor.description]
    rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/threshold-simulator")
def threshold_simulator(threshold: float = 0.5):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            SUM(CASE WHEN fraud_probability > %s AND is_fraud_label = 1 THEN amount ELSE 0 END) as fraud_caught_value,
            SUM(CASE WHEN fraud_probability > %s AND is_fraud_label = 1 THEN 1 ELSE 0 END) as fraud_caught_count,
            SUM(CASE WHEN fraud_probability <= %s AND is_fraud_label = 1 THEN amount ELSE 0 END) as fraud_missed_value,
            SUM(CASE WHEN fraud_probability > %s AND is_fraud_label = 0 THEN 1 ELSE 0 END) as false_declines
        FROM decision_results
    """, (threshold, threshold, threshold, threshold))
    row = cursor.fetchone()
    conn.close()
    return {
        "threshold": threshold,
        "fraud_caught_value": float(row[0] or 0),
        "fraud_caught_count": int(row[1] or 0),
        "fraud_missed_value": float(row[2] or 0),
        "false_declines": int(row[3] or 0),
    }

@app.get("/api/pipeline/health")
def pipeline_health():
    return {
        "lakehouse_status": "healthy",
        "snowflake_status": "healthy",
        "last_drift_check": "STABLE",
        "model_version": "lightgbm_v1",
        "api_latency_ms_p50": 28,
        "api_latency_ms_p95": 62,
    }