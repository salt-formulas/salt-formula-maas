{%- from "maas/map.jinja" import mirror with context %}

{%- if mirror.get('enabled') %}

{%- if mirror.get('image') %}

maas_mirror_packages:
  pkg.installed:
    - names: {{ mirror.pkgs }}

{%- for release_name, release in mirror.image.release.iteritems() %}

mirror_image_{{ release_name }}:
  cmd.run:
  - name: "sstream-mirror --keyring={{ release.keyring }} {{ release.upstream }} {{ release.local_dir }} {%- if release.get('arch') %} 'arch={{ release.arch }}'{%- endif %} {%- if release.get('subarch') %} 'subarch~({{ release.subarch }})'{%- endif %} 'release~({{ release_name }})' {%- if release.get('count') %} --max={{ release.count }}{%- endif %}"
  - require:
    - pkg: maas_mirror_packages

{%- endfor %}

{%- endif %}

{%- endif %}
