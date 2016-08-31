{%- from "maas/map.jinja" import region with context %}
{%- if region.enabled %}

maas_region_packages:
  pkg.installed:
    - names: {{ region.pkgs }}

/etc/maas/regiond.conf:
  file.managed:
  - source: salt://maas/files/regiond.conf
  - template: jinja
  - require:
    - pkg: maas_region_packages

/etc/maas/preseeds/curtin_userdata_amd64_generic_trusty:
  file.managed:
  - source: salt://maas/files/curtin_userdata_amd64_generic_trusty
  - template: jinja
  - user: root
  - group: root
  - mode: 644
  - require:
    - pkg: maas_region_packages

maas_region_services:
  service.running:
  - enable: true
  - names: {{ region.services }}
  - require:
    - cmd: maas_region_syncdb
  - watch:
    - file: /etc/maas/regiond.conf

maas_region_syncdb:
  cmd.run:
  - names:
    - maas-region syncdb
  - require:
    - file: /etc/maas/regiond.conf

maas_set_admin_passord:
  cmd.run:
  - name: "maas createadmin --username {{ region.admin.username }} --password {{ region.admin.password }} --email {{ region.admin.email }} && touch /var/lib/maas/.setup_admin"
  - creates: /var/lib/maas/.setup_admin
  - require:
    - service: maas_region_services

{%- endif %}