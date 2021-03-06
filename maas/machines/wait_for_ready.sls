{%- from "maas/map.jinja" import region with context %}

maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"

wait_for_machines_ready:
  module.run:
  - name: maas.wait_for_machine_status
  - require:
    - cmd: maas_login_admin
