postgresql:
  server:
    enabled: true
    clients:
    - 127.0.0.1
    bind:
      address: 127.0.0.1
      port: 5432
      protocol: tcp
    database:
      maasdb:
        enabled: true
        encoding: 'UTF8'
        locale: 'en_US'
        users:
        - name: maas
          password: password
          host: localhost
          createdb: true
          rights: all privileges
