import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from pyiceberg.catalog import load_catalog

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

# Pull data back from the lakehouse — proving Phase 1's table is genuinely usable
catalog = load_catalog("riskflow", **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"})
table = catalog.load_table("riskflow_lakehouse.raw_transactions")
df = table.scan().to_pandas()

print("Loaded from lakehouse:", df.shape)

# Encode categorical columns as integer codes — LightGBM needs numeric input
categorical_cols = ["ProductCD", "card4", "card6", "P_emaildomain", "DeviceType", "DeviceInfo"]
for col in categorical_cols:
    df[col] = df[col].astype("category").cat.codes

feature_cols = ["amount", "card1", "addr1"] + categorical_cols
X = df[feature_cols]
y = df["is_fraud_label"]

# Stratified split — preserves the same ~3.5% fraud rate in both train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")
print(f"Train fraud rate: {y_train.mean():.4%} | Test fraud rate: {y_test.mean():.4%}")

model = lgb.LGBMClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# AUC, not accuracy — accuracy is meaningless on a 3.5% fraud rate, as Phase 1 proved
probs = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, probs)
print(f"\nTest AUC: {auc:.4f}")

# Save the trained model for the next script to use
import joblib
joblib.dump(model, "backend/fraud_model.pkl")
print("Model saved to backend/fraud_model.pkl")