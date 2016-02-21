{%- if pillar.maas is defined %}
include:
{%- if pillar.maas.server is defined %}
- maas.server
{%- endif %}
{%- endif %}
