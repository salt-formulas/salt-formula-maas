{%- from "maas/map.jinja" import server with context %}
{%- if server.enabled %}

mass_server_packages:
  pkg.installed:
    - names: {{ server.pkgs }}

{%- endif %}
