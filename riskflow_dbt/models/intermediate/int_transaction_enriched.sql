with daily_amounts as (
    select
        card1,
        txn_date,
        amount,
        txn_timestamp,
        lag(amount) over (partition by card1 order by txn_timestamp) as prev_amount,
        avg(amount) over (
            partition by card1
            order by txn_timestamp
            rows between 6 preceding and current row
        ) as rolling_avg_amount_7txn
    from {{ ref('stg_transactions') }}
)

select
    *,
    case
        when prev_amount is not null and prev_amount != 0
        then (amount - prev_amount) / prev_amount
        else null
    end as pct_change_from_prev_txn
from daily_amounts
