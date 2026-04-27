{{
  config(
    materialized='view'
  )
}}

select
    building_id,
    device_id,
    event_date,
    count(*) as events_received,
    countif(had_negative_energy) as invalid_negative_energy_events,
    countif(had_null_metric) as null_metric_events,
    countif(status_normalized = 'offline') as offline_events,
    round(safe_divide(countif(had_null_metric), count(*)), 4) as null_ratio
from {{ ref('stg_iot_energy_events') }}
group by 1, 2, 3
