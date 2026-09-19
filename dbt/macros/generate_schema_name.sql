{% macro generate_schema_name(custom_schema_name, node) -%}
    {# Keep the teaching project's layers as RAW/STAGING/INTERMEDIATE/ANALYTICS.
       Production teams commonly add target-specific prefixes to avoid collisions. #}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
