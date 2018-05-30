rsyslog:
  #server:
    #enabled: true
  client:
    enabled: true
    #output:
      #file:
        #/var/log/syslog:
          #filter: "*.*;auth,authpriv.none"
          #owner: syslog
          #group: adm
          #createmode: 0640
          #umask: 0022
