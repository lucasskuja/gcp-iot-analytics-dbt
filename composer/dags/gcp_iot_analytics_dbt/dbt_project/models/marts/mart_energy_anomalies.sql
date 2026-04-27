{{
  config(
    materialized='table',
    partition_by={'field': 'event_date', 'data_type': 'date'},
    cluster_by=['building_id', 'device_id']
  )
}}

with hourly as (
    select * from {{ ref('int_device_hourly_energy') }}
),

stats as (
    select
        building_id,
        device_id,
        avg(avg_energy_kwh) as mean_energy_kwh,
        stddev(avg_energy_kwh) as stddev_energy_kwh
    from hourly
    group by 1, 2
)

select
    h.building_id,
    h.device_id,
    date(h.event_hour) as event_date,
    h.event_hour,
    h.avg_energy_kwh,
    s.mean_energy_kwh,
    s.stddev_energy_kwh,
    safe_divide(h.avg_energy_kwh - s.mean_energy_kwh, nullif(s.stddev_energy_kwh, 0)) as z_score,
    case
        when abs(safe_divide(h.avg_energy_kwh - s.mean_energy_kwh, nullif(s.stddev_energy_kwh, 0))) >= 2 then true
        else false
    end as is_anomaly
from hourly h
left join stats s
  using (building_id, device_id)
