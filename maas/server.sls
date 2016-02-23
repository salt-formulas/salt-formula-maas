{%- from "maas/map.jinja" import server with context %}
{%- if server.enabled %}

mass_server_packages:
  pkg.installed:
    - names: {{ server.pkgs }}

/etc/maas/preseeds/curtin_userdata_amd64_generic_trusty:
  file.managed:
  - source: salt://maas/files/curtin_userdata_amd64_generic_trusty
  - template: jinja
  - user: root
  - group: root
  - mode: 644
  - require:
    - pkg: mass_server_packages

{%- endif %}
