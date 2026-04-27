{% macro normalize_status(column_name) -%}
  case
    when lower({{ column_name }}) in ('online', '1', 'true') then 'online'
    when lower({{ column_name }}) in ('offline', '0', 'false') then 'offline'
    else 'unknown'
  end
{%- endmacro %}
