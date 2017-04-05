{%- from "maas/map.jinja" import region with context %}

maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"

create__machines:
  module.run:
  - name: maas.process_machines
  - require:
    - cmd: maas_login_admin
