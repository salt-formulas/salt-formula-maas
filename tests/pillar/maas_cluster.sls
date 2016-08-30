maas:
  cluster:
    enabled: true
    role: slave
    region:
      port: 80
      host: localhost
  region:
    bind:
      host: localhost
      port: 80
    database:
      engine: postgresql
      host: localhost
      name: maasdb
      password: password
      username: maas
    enabled: true