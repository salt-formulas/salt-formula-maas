maas:
  cluster:
    enabled: true
    region:
      host: localhost
    role: master
  region:
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
