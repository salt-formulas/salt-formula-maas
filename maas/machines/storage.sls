{%- from "maas/map.jinja" import region with context %}


maas_login_admin:
  cmd.run:
  - name: "maas-region apikey --username {{ region.admin.username }} > /var/lib/maas/.maas_credentials"


{%- for machine_name, machine in region.machines.iteritems() %}

{%- if machine.disk_layout is defined %}

{%- if machine.disk_layout.type is defined %}

maas_machines_storage_{{ machine_name }}_{{ machine.disk_layout.type }}:
  maasng.disk_layout_present:
    - hostname: {{ machine_name }}
    - layout_type: {{ machine.disk_layout.type }}
    {%- if machine.disk_layout.root_size is defined %}
    - root_size: {{ machine.disk_layout.root_size }}
    {%- endif %}
    {%- if machine.disk_layout.root_device is defined %}
    - root_device: {{ machine.disk_layout.root_device }}
    {%- endif %}
    {%- if machine.disk_layout.volume_group is defined %}
    - volume_group: {{ machine.disk_layout.volume_group }}
    {%- endif %}
    {%- if machine.disk_layout.volume_name is defined %}
    - volume_name: {{ machine.disk_layout.volume_name }}
    {%- endif %}
    {%- if machine.disk_layout.volume_size is defined %}
    - volume_size: {{ machine.disk_layout.volume_size }}
    {%- endif %}
    - require:
      - cmd: maas_login_admin

{%- endif %}

{%- if machine.disk_layout.bootable_device is defined %}

maas_machines_storage_set_bootable_disk_{{ machine_name }}_{{ machine.disk_layout.bootable_device }}:
  maasng.select_boot_disk:
  - name: {{ machine.disk_layout.bootable_device }}
  - hostname: {{ machine_name }}
  - require:
    - cmd: maas_login_admin

{%- endif %}

{%- if machine.disk_layout.disk is defined %}

{%- for disk_name, disk in machine.disk_layout.disk.iteritems() %}

{%- if disk.type == "physical" %}

maas_machine_{{ machine_name }}_{{ disk_name }}:
  maasng.disk_partition_present:
    - hostname: {{ machine_name }}
    - name: {{ disk_name }}
    - partition_schema: {{ disk.get("partition_schema", {}) }}

{%- endif %}

{%- if disk.type == "raid" %}

maas_machine_{{ machine_name }}_{{ disk_name }}:
  maasng.raid_present:
    - hostname: {{ machine_name }}
    - name: {{ disk_name }}
    - level: {{ disk.level }}
    - devices: {{ disk.get("devices", []) }}
    - partitions: {{ disk.get("partitions", []) }}
    - partition_schema: {{ disk.get("partition_schema", {}) }}
    - require:
      - cmd: maas_login_admin
    {%- if disk.devices is defined %}
    {%- for device_name in disk.devices %}
      {%- if salt['pillar.get']('maas:region:machines:'+machine_name+':disk_layout:disk:'+device_name) is mapping %}
      - maasng: maas_machine_{{ machine_name }}_{{ device_name }}
      {%- endif %}
    {%- endfor %}
    {%- endif %}
    {%- if disk.partitions is defined %}
    {%- for partition in disk.partitions %}
      {% set device_name = partition.split('-')[0] %}
      {%- if salt['pillar.get']('maas:region:machines:'+machine_name+':disk_layout:disk:'+device_name) is mapping %}
      - maasng: maas_machine_{{ machine_name }}_{{ device_name }}
      {%- endif %}
    {%- endfor %}
    {%- endif %}
{%- endif %}

{%- if disk.type == "lvm" %}

maas_machine_vg_{{ machine_name }}_{{ disk_name }}:
  maasng.volume_group_present:
    - hostname: {{ machine_name }}
    - name: {{ disk_name }}
    {%- if disk.devices is defined %}
    - devices: {{ disk.devices }}
    {%- endif %}
    {%- if disk.partitions is defined %}
    - partitions: {{ disk.partitions }}
    {%- endif %}
    - require:
      - cmd: maas_login_admin
    {%- if disk.partitions is defined %}
    {%- for partition in disk.partitions %}
      {% set device_name = partition.split('-')[0] %}
      {%- if salt['pillar.get']('maas:region:machines:'+machine_name+':disk_layout:disk:'+device_name) is mapping %}
      - maasng: maas_machine_{{ machine_name }}_{{ device_name }}
      {%- endif %}
    {%- endfor %}
    {%- endif %}
    {%- if disk.devices is defined %}
    {%- for device_name in disk.devices %}
      {%- if salt['pillar.get']('maas:region:machines:'+machine_name+':disk_layout:disk:'+device_name) is mapping %}
      - maasng: maas_machine_{{ machine_name }}_{{ device_name }}
      {%- endif %}
    {%- endfor %}
    {%- endif %}

{%- for volume_name, volume in disk.volume.iteritems() %}

maas_machine_volume_{{ machine_name }}_{{ disk_name }}_{{ volume_name }}:
  maasng.volume_present:
    - hostname: {{ machine_name }}
    - name: {{ volume_name }}
    - volume_group_name: {{ disk_name }}
    - size: {{ volume.size }}
    {%- if volume.type is defined %}
    - type: {{ volume.type }}
    {%- endif %}
    {%- if volume.mount is defined %}
    - mount: {{ volume.mount }}
    {%- endif %}
    - require:
      - maasng: maas_machine_vg_{{ machine_name }}_{{ disk_name }}

{%- endfor %}

{%- endif %}

{%- endfor %}

{%- endif %}

{%- endif %}

{%- endfor %}

