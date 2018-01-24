maas:
  region:
    theme: theme
    bind:
      host: localhost
      port: 80
    admin:
      username: admin
      password: password
      email:  email@example.com
    database:
      engine: postgresql
      host: localhost
      name: maasdb
      password: password
      username: maas
    enabled: true
    salt_master_ip: 127.0.0.1
    machines:
      server3:
        disk_layout:
          type: flat
          bootable_device: vda
          disk:
            vda:
              type: physical
              partition_schema:
                part1:
                  size: 10G
                  type: ext4
                  mount: '/'
                part2:
                  size: 2G
                part3:
                  size: 3G
            vdc:
              type: physical
              partition_schema:
                part1:
                  size: 100%
            vdd:
              type: physical
              partition_schema:
                part1:
                  size: 100%
            raid0:
              type: raid
              level: 10
              devices:
                - vde
                - vdf
              partition_schema:
                part1:
                  size: 10G
                part2:
                  size: 2G
                part3:
                  size: 3G
            raid1:
              type: raid
              level: 1
              partitions:
                - vdc-part1
                - vdd-part1
            volume_group2:
              type: lvm
              devices:
                - raid1
              volume:
                tmp:
                  size: 5G
                  fs_type: ext4
                  mount: '/tmp'
                log:
                  size: 7G
                  fs_type: ext4
                  mount: '/var/log'
