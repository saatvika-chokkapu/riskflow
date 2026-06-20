select
    txn_id,
    transactiondt as transaction_dt,
    amount,
    productcd as product_cd,
    card1,
    card4,
    card6,
    addr1,
    p_emaildomain as email_domain,
    devicetype as device_type,
    deviceinfo as device_info,
    is_fraud_label,
    txn_timestamp,
    txn_date
from {{ source('riskflow_raw', 'raw_transactions') }}