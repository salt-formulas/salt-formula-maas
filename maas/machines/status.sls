{%- from "maas/map.jinja" import region with context %}

maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"

check_machines_status:
  module.run:
  - name: maas.machines_status
  - require:
    - cmd: maas_login_admin
