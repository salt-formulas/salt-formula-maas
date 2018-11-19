maas:
  cluster:
    enabled: true
    region:
      host: localhost
      port: 80
    role: master
    enable_iframe: True
    cluster:
      curtin_vars:
        amd64:
          xenial:
            extra_pkgs: [ "curl", "wget" ]
            #kernel_package: 'linux-image-virtual-hwe-16.04'
            kernel_package: 'mc'
  region:
    enabled: true
    bind:
      host: localhost
      port: 80
    theme: theme
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
    salt_master_ip: 127.0.0.1
