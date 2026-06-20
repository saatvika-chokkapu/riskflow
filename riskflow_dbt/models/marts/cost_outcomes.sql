select
    txn_date,
    count(*) as total_transactions,

    sum(case when is_fraud_label = 1 then 1 else 0 end) as total_fraud_transactions,
    sum(case when riskflow_decision = 'decline' and is_fraud_label = 1 then 1 else 0 end) as riskflow_fraud_caught,
    sum(case when riskflow_decision = 'decline' and is_fraud_label = 0 then 1 else 0 end) as riskflow_false_declines,
    sum(riskflow_cost) as riskflow_total_cost,

    sum(case when naive_decision = 'decline' and is_fraud_label = 1 then 1 else 0 end) as naive_fraud_caught,
    sum(case when naive_decision = 'decline' and is_fraud_label = 0 then 1 else 0 end) as naive_false_declines,
    sum(naive_cost) as naive_total_cost,

    sum(naive_cost) - sum(riskflow_cost) as net_cost_vs_naive_baseline

from {{ ref('stg_decisions') }}
group by txn_date
order by txn_date
