{%- from "maas/map.jinja" import region with context %}
{%- if region.enabled %}

maas_region_packages:
  pkg.installed:
    - names: {{ region.pkgs }}

/etc/maas/regiond.conf:
  file.managed:
  - source: salt://maas/files/regiond.conf
  - template: jinja
  - group: maas
  - require:
    - pkg: maas_region_packages

/usr/lib/python3/dist-packages/provisioningserver/templates/proxy/maas-proxy.conf.template:
  file.managed:
  - source: salt://maas/files/maas-proxy.conf.template
  - template: jinja
  - require:
    - pkg: maas_region_packages

{%- if region.database.initial_data is defined %}

/root/maas/scripts/restore_{{ region.database.name }}.sh:
  file.managed:
    - source: salt://maas/files/restore.sh
    - mode: 770
    - template: jinja

restore_maas_database_{{ region.database.name }}:
  cmd.run:
  - name: /root/maas/scripts/restore_{{ region.database.name }}.sh
  - unless: "[ -f /root/maas/flags/{{ region.database.name }}-installed ]"
  - cwd: /root
  - require:
    - file: /root/maas/scripts/restore_{{ region.database.name }}.sh

{%- endif %}

{%- if region.get('enable_iframe', False)  %}

/etc/apache2/conf-enabled/maas-http.conf:
  file.managed:
  - source: salt://maas/files/maas-http.conf
  - user: root
  - group: root
  - mode: 644
  - require:
    - pkg: maas_region_packages
  - require_in:
    - service: maas_region_services

maas_apache_headers:
  cmd.run:
  - name: "a2enmod headers"
  - require:
    - pkg: maas_region_packages
  - require_in:
    - service: maas_region_services

{%- endif %}

{% if region.theme is defined %}

/usr/share/maas/web/static/css/maas-styles.css:
  file.managed:
  - source: salt://maas/files/{{ region.theme }}-styles.css
  - mode: 644
  - watch_in:
    - service: maas_region_services

{%- endif %}

/etc/maas/preseeds/curtin_userdata_amd64_generic_trusty:
  file.managed:
  - source: salt://maas/files/curtin_userdata_amd64_generic_trusty
  - template: jinja
  - user: root
  - group: root
  - mode: 644
  - context:
      salt_master_ip: {{ region.salt_master_ip }}
  - require:
    - pkg: maas_region_packages

/etc/maas/preseeds/curtin_userdata_amd64_generic_xenial:
  file.managed:
  - source: salt://maas/files/curtin_userdata_amd64_generic_xenial
  - template: jinja
  - user: root
  - group: root
  - mode: 644
  - context:
      salt_master_ip: {{ region.salt_master_ip }}
  - require:
    - pkg: maas_region_packages

/root/.pgpass:
  file.managed:
  - source: salt://maas/files/pgpass
  - template: jinja
  - user: root
  - group: root
  - mode: 600

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

maas_set_admin_password:
  cmd.run:
  - name: "maas createadmin --username {{ region.admin.username }} --password {{ region.admin.password }} --email {{ region.admin.email }} && touch /var/lib/maas/.setup_admin"
  - creates: /var/lib/maas/.setup_admin
  - require:
    - service: maas_region_services

maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"

maas_config:
  module.run:
  - name: maas.process_maas_config
  - require:
    - cmd: maas_login_admin

{%- if region.get('commissioning_scripts', False)  %}
/etc/maas/files/commisioning_scripts/:
  file.directory:
  - user: root
  - group: root
  - mode: 755
  - makedirs: true
  - require:
    - pkg: maas_region_packages

/etc/maas/files/commisioning_scripts/00-maas-05-simplify-network-interfaces:
  file.managed:
  - source: salt://maas/files/commisioning_scripts/00-maas-05-simplify-network-interfaces
  - mode: 755
  - user: root
  - group: root
  - require:
    - file: /etc/maas/files/commisioning_scripts/

maas_commissioning_scripts:
  module.run:
  - name: maas.process_commissioning_scripts
  - require:
    - module: maas_config
{%- endif %}

{%- if region.get('fabrics', False)  %}
maas_fabrics:
  module.run:
  - name: maas.process_fabrics
  - require:
    - module: maas_config
{%- endif %}

{%- if region.get('subnets', False)  %}
maas_subnets:
  module.run:
  - name: maas.process_subnets
  - require:
    - module: maas_config
    {%- if region.get('fabrics', False)  %}
    - module: maas_fabrics
    {%- endif %}
{%- endif %}

{%- if region.get('devices', False)  %}
maas_devices:
  module.run:
  - name: maas.process_devices
  - require:
    - module: maas_config
    {%- if region.get('subnets', False)  %}
    - module: maas_subnets
    {%- endif %}
{%- endif %}

{%- if region.get('boot_sources', False)  %}
maas_boot_sources:
  module.run:
  - name: maas.process_boot_sources
  - require:
    - module: maas_config
{%- endif %}

{%- if region.get('dhcp_snippets', False)  %}
maas_dhcp_snippets:
  module.run:
  - name: maas.process_dhcp_snippets
  - require:
    - module: maas_config
{%- endif %}

{%- if region.get('package_repositories', False)  %}
maas_package_repositories:
  module.run:
  - name: maas.process_package_repositories
  - require:
    - module: maas_config
{%- endif %}

{%- if region.get('boot_resources', False)  %}
maas_boot_resources:
  module.run:
  - name: maas.process_boot_resources
  - require:
    - module: maas_config
{%- endif %}

maas_domain:
  module.run:
  - name: maas.process_domain
  - require:
    - module: maas_config

{%- if region.get('sshprefs', False)  %}
maas_sshprefs:
  module.run:
  - name: maas.process_sshprefs
  - require:
    - module: maas_config
{%- endif %}

{%- endif %}
