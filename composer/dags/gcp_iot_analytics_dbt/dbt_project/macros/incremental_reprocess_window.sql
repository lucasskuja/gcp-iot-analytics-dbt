{% macro incremental_reprocess_window(column_name, days_back=2) -%}
  {% if is_incremental() %}
    and {{ column_name }} >= timestamp_sub(
      (select coalesce(max({{ column_name }}), timestamp('1970-01-01')) from {{ this }}),
      interval {{ days_back }} day
    )
  {% endif %}
{%- endmacro %}
