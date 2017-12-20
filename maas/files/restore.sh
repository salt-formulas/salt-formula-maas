{%- from "maas/map.jinja" import region with context}

{%- set database = region.get("database", {}) %}

{%- if database.host is defined %}
{%- set pghost = database.get("host", "") %}
export PGHOST={{ pghost }}
{%- endif %}
{%- if database.user is defined %}
{%- set pguser = database.get("user", "") %}
export PGUSER={{ pguser }}
{%- endif %}
export PGPASSFILE=/root/.pgpass

{%- set db_name = database.get("name", "maasdb") %}
{%- set backupninja_host = database.initial_data.get("host", grains.id ) %}
{%- if database.initial_data.age is defined %}
{%- set age = database.initial_data.get("age", "0") %}
{%- else %}{%- set age = "0" %}{%- endif %}
{%- set backupninja_source = database.initial_data.get("source", "cfg01.local")%}
{%- set source_name = db_name + ".pg_dump.gz" %}
{%- set dest_name = db_name + ".pg_dump.gz" %}
{%- set target = "/root/postgresql/data/" %}


scp backupninja@{{ backupninja_host }}:/srv/backupninja/{{ backupninja_source }}/var/backups/postgresql/postgresql.{{ age }}/{{ source_name }} {{ target }}{{ dest_name }} 
gunzip -d -1 -f {{ target }}{{ dest_name }}

scp -r backupninja@{{ backupninja_host }}:/srv/backupninja/{{ backupninja_source }}/etc/maas/maas.{{ age }} /etc/maas
scp -r backupninja@{{ backupninja_host }}:/srv/backupninja/{{ backupninja_source }}/var/lib/maas/maas.{{ age }} /var/lib/maas

sudo systemctl stop maas-dhcpd.service
sudo systemctl stop maas-rackd.service
sudo systemctl stop maas-regiond.service

pg_restore {{ target }}{{ db_name }}.pg_dump --dbname={{ db_name }} --no-password -c

touch /root/maas/flags/{{ db_name }}-installed

sudo systemctl start maas-dhcpd.service
sudo systemctl start maas-rackd.service
sudo systemctl start maas-regiond.service