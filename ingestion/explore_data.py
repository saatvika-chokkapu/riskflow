import pandas as pd

# Load both files
transactions = pd.read_csv("data/raw/train_transaction.csv")
identity = pd.read_csv("data/raw/train_identity.csv")

print("Transaction file shape:", transactions.shape)
print("Identity file shape:", identity.shape)

# Left join: every transaction matters, even ones with no identity data
merged = transactions.merge(identity, on="TransactionID", how="left")

print("\nMerged shape:", merged.shape)
print("Transactions WITH identity data:", merged["DeviceType"].notna().sum())
print("Transactions WITHOUT identity data:", merged["DeviceType"].isna().sum())

# Fraud label distribution
fraud_count = merged["isFraud"].sum()
total = len(merged)
fraud_rate = fraud_count / total

print(f"\nTotal transactions: {total:,}")
print(f"Fraud transactions: {fraud_count:,}")
print(f"Fraud rate: {fraud_rate:.4%}")