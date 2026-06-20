import time
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from backend.cost_model import assign_segment, decide_transaction

app = FastAPI(title="RiskFlow Decisioning API")

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

    latency_ms = (time.perf_counter() - start_time) * 1000

    return {
        "txn_id": txn.txn_id,
        "decision": decision,
        "fraud_probability": round(float(fraud_probability), 4),
        "segment": segment,
        "expected_cost_approve": round(cost_approve, 2),
        "expected_cost_decline": round(cost_decline, 2),
        "latency_ms": round(latency_ms, 2),
    }