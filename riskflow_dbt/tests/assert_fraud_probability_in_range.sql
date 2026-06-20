select *
from {{ ref('stg_decisions') }}
where fraud_probability < 0 or fraud_probability > 1
