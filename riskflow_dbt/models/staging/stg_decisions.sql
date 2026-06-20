select
    txn_id,
    txn_date,
    card1,
    segment,
    amount,
    is_fraud_label,
    fraud_probability,
    riskflow_decision,
    riskflow_cost,
    naive_decision,
    naive_cost
from {{ source('riskflow_raw', 'decision_results') }}