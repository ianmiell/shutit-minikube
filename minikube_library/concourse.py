def do_concourse(s):
	s.send('rm -rf tmp_concourse && mkdir -p tmp_concourse && cd tmp_concourse')
	s.send('git clone https://github.com/helm/charts')
	s.send('cd charts/stable/concourse')
	s.send_file('custom_values.yaml','''## Default values for Concourse Helm Chart.
## This is a YAML-formatted file.
## Declare variables to be passed into your templates.

## Override the name of the Chart.
##
# nameOverride:

## Concourse image.
##
image: concourse/concourse

## Concourse image version.
## ref: https://hub.docker.com/r/concourse/concourse/tags/
##
imageTag: "4.2.2"

## Specific image digest to use in place of a tag.
## ref: https://kubernetes.io/docs/concepts/configuration/overview/#container-images
##
# imageDigest: sha256:54ea351808b55ecc14af6590732932e2a6a0ed8f6d10f45e8be3b51165d5526a

## Specify a imagePullPolicy: 'Always' if imageTag is 'latest', else set to 'IfNotPresent'.
## ref: https://kubernetes.io/docs/user-guide/images/#pre-pulling-images
##
imagePullPolicy: IfNotPresent

## Configuration values for Concourse.
## ref: https://concourse-ci.org/setting-up.html
##
concourse:
  web:
    ## Minimum level of logs to see.
    logLevel: debug
    ## IP address on which to listen for web traffic.
    bindIp: 0.0.0.0
    ## Port on which to listen for HTTP traffic.
    bindPort: 8080
    ## Port on which to listen for HTTPS traffic.
    # tlsBindPort:
    ## File containing an SSL certificate.
    # tlsCert:
    ## File containing an RSA private key, used to encrypt HTTPS traffic.
    # tlsKey:
    ## URL used to reach any ATC from the outside world.
    externalUrl: http://127.0.0.1:8080
    ## URL used to reach this ATC from other ATCs in the cluster.
    peerUrl: http://127.0.0.1:8080
    ## Enable encryption of pipeline configuration. Encryption keys can be set via secrets.
    ## See https://concourse-ci.org/encryption.html
    ##
    encryption:
      enabled: false
    localAuth:
      enabled: true
    ## IP address on which to listen for the pprof debugger endpoints.
    # debugBindIp: 127.0.0.1
    ## Port on which to listen for the pprof debugger endpoints.
    # debugBindPort: 8079
    ## Length of time for a intercepted session to be idle before terminating.
    # interceptIdleTimeout: 0m
    ## Time limit on checking for new versions of resources.
    # globalResourceCheckTimeout: 1h
    ## Interval on which to check for new versions of resources.
    # resourceCheckingInterval: 1m
    ## Interval on which to check for new versions of resource types.
    # resourceTypeCheckingInterval: 1m
    ## Method by which a worker is selected during container placement.
    # containerPlacementStrategy: volume-locality
    ## How long to wait for Baggageclaim to send the response header.
    # baggageclaimResponseHeaderTimeout: 1m
    ## Directory containing downloadable CLI binaries.
    # cliArtifactsDir:
    ## Log database queries.
    # logDbQueries:
    ## Interval on which to run build tracking.
    # buildTrackerInterval: 10s
    ## Default build logs to retain, 0 means all
    # defaultBuildLogsToRetain:
    ## Maximum build logs to retain, 0 means not specified. Will override values configured in jobs
    # maxBuildLogsToRetain:
    ## Default max number of cpu shares per task, 0 means unlimited
    # defaultTaskCpuLimit:
    ## Default maximum memory per task, 0 means unlimited
    # defaultTaskMemoryLimit:
    postgres:
      ## The host to connect to.
      host: 127.0.0.1
      ## The port to connect to.
      port: 5432
      ## Path to a UNIX domain socket to connect to.
      # socket:
      ## Whether or not to use SSL.
      sslmode: disable
      ## Dialing timeout. (0 means wait indefinitely)
      connectTimeout: 5m
      ## The name of the database to use.
      database: atc

    kubernetes:

      ## Enable the use of in-cluster Kubernetes Secrets.
      ##
      enabled: true

      ## Prefix to use for Kubernetes namespaces under which secrets will be looked up. Defaults to
      ## the Release name hyphen, e.g. "my-release-" produces namespace "my-release-main" for the
      ## "main" Concourse team.
      ##
      ## namespacePrefix:

      ## Teams to create namespaces for to hold secrets.
      teams:
        - main

      ## When true, namespaces are not deleted when the release is deleted.

      keepNamespaces: true

      ## Path to Kubernetes config when running ATC outside Kubernetes.
      # configPath:

    awsSecretsManager:
      ## Enable the use of AWS Secrets Manager.
      ##
      enabled: false

      ## AWS region to use when reading from Secrets Manager
      ##
      # region:

      ## pipeline-specific template for Secrets Manager parameters, defaults to: /concourse/{team}/{pipeline}/{secret}
      ##
      # pipelineSecretTemplate:

      ## team-specific template for Secrets Manager parameters, defaults to: /concourse/{team}/{secret}
      ##
      # teamSecretTemplate: ''

    awsSsm:
      ## Enable the use of AWS SSM.
      ##
      enabled: false

      ## AWS region to use when reading from SSM
      ##
      # region:

      ## pipeline-specific template for SSM parameters, defaults to: /concourse/{team}/{pipeline}/{secret}
      ##
      # pipelineSecretTemplate:

      ## team-specific template for SSM parameters, defaults to: /concourse/{team}/{secret}
      ##
      # teamSecretTemplate: ''


    vault:
      enabled: false

      ## URL pointing to vault addr (i.e. http://vault:8200).
      ##
      # url:

      ## vault path under which to namespace credential lookup, defaults to /concourse.
      ##
      pathPrefix: /concourse

      ## if the Vault server is using a self-signed certificate, set this to true,
      ## and provide a value for the cert in secrets.
      ##
      # useCaCert:

      ## vault authentication backend, leave this blank if using an initial periodic token
      ## currently supported backends: token, approle, cert.
      ##
      # authBackend:

      ## Cache returned secrets for their lease duration in memory
      # cache:
      ## If the cache is enabled, and this is set, override secrets lease duration with a maximum value
      # maxLease:
      ## Path to a directory of PEMEncoded CA cert files to verify the vault server SSL cert.
      # caPath:
      ## If set, is used to set the SNI host when connecting via TLS.
      # serverName:
      ## Enable insecure SSL verification.
      # insecureSkipVerify:
        ## Client token for accessing secrets within the Vault server.
        # clientToken:
      ## Auth backend to use for logging in to Vault.
      # authBackend:
      ## Time after which to force a reLogin. If not set, the token will just be continuously renewed.
      # authBackendMaxTtl:
      ## The maximum time between retries when logging in or reAuthing a secret.
      retryMax: 5m
      ## The initial time between retries when logging in or reAuthing a secret.
      retryInitial: 1s
    ## Don't actually do any automatic scheduling or checking.
    # noop:
    staticWorker:
      enabled: false
      ## A Garden API endpoint to register as a worker.
      gardenUrl:
      ## A Baggageclaim API endpoint to register with the worker.
      baggageclaimUrl:
      ## A resource type to advertise for the worker. Can be specified multiple times.
      resource:
    metrics:
      ## Host string to attach to emitted metrics.
      hostName:
      ## A keyValue attribute to attach to emitted metrics. Can be specified multiple times.
      attribute:
    datadog:
      enabled: false
      ## Use IP of node the pod is scheduled on, overrides `agentHost`
      agentHostUseHostIP: false
      ## Datadog agent host to expose dogstatsd metrics
      agentHost: 127.0.0.1
      ## Datadog agent port to expose dogstatsd metrics
      agentPort: 8125
      ## Prefix for all metrics to easily find them in Datadog
      # prefix: concoursedev
    influxdb:
      enabled: false
      ## InfluxDB server address to emit points to.
      url: http://127.0.0.1:8086
      ## InfluxDB database to write points to.
      database: concourse
      ## InfluxDB server username.
      # username:
      ## Skip SSL verification when emitting to InfluxDB.
      insecureSkipVerify: false
    ## Emit metrics to logs.
    # emitToLogs:
    newrelic:
      enabled: false
      ## New Relic Account ID
      # accountId:
      ## New Relic Insights API Key
      # apiKey:
      ## An optional prefix for emitted New Relic events
      # servicePrefix:
    prometheus:
      enabled: false
      ## IP to listen on to expose Prometheus metrics.
      bindIp: "0.0.0.0"
      ## Port to listen on to expose Prometheus metrics.
      bindPort: 9391
    riemann:
      enabled: false
      ## Riemann server address to emit metrics to.
      # host:
      ## Port of the Riemann server to emit metrics to.
      port: 5555
      ## An optional prefix for emitted Riemann services
      # servicePrefix:
      ## Tag to attach to emitted metrics. Can be specified multiple times.
      # tag:
    ## The value to set for XFrame-Options. If omitted, the header is not set.
    # xFrameOptions:
    gc:
      overrideDefaults: false
      ## Interval on which to perform garbage collection.
      interval: 30s
      ## Grace period before reaping oneOff task containers
      oneOffGracePeriod: 5m
    syslog:
      enabled: false
      ## Client hostname with which the build logs will be sent to the syslog server.
      hostName: atc-syslog-drainer
      ## Remote syslog server address with port (Example: 0.0.0.0:514).
      # address:
      ## Transport protocol for syslog messages (Currently supporting tcp, udp & tls).
      # transport:
      ## Interval over which checking is done for new build logs to send to syslog server (duration measurement units are s/m/h; eg. 30s/30m/1h)
      drainInterval: 30s
      ## if the syslog server is using a self-signed certificate, set this to true,
      ## and provide a value for the cert in secrets.
      useCaCert: false
    auth:
      ## Force sending secure flag on http cookies
      # cookieSecure:
      ## Length of time for which tokens are valid. Afterwards, users will have to log back in.
      # duration: 24h
      mainTeam:
        ## List of whitelisted local concourse users. These are the users you've added at atc startup with the addLocalUser setting.
        localUser: "test"
        ## Setting this flag will whitelist all logged in users in the system. ALL OF THEM. If, for example, you've configured GitHub, any user with a GitHub account will have access to your team.
        # allowAllUsers:
        ## Authentication (Main Team) (CloudFoundry)
        cf:
          ## List of whitelisted CloudFoundry users.
          user:
          ## List of whitelisted CloudFoundry orgs
          org:
          ## List of whitelisted CloudFoundry spaces
          space:
          ## (Deprecated) List of whitelisted CloudFoundry space guids
          spaceGuid:
        ## Authentication (Main Team) (GitHub)
        github:
          ## List of whitelisted GitHub users
          user:
          ## List of whitelisted GitHub orgs
          org:
          ## List of whitelisted GitHub teams
          team:
        ## Authentication (Main Team) (GitLab)
        gitlab:
          ## List of whitelisted GitLab users
          user:
          ## List of whitelisted GitLab groups
          group:
        ## Authentication (Main Team) (LDAP)
        ldap:
          ## List of whitelisted LDAP users
          user:
          ## List of whitelisted LDAP groups
          group:
        ## Authentication (Main Team) (OAuth2)
        oauth:
          ## List of whitelisted OAuth2 users
          user:
          ## List of whitelisted OAuth2 groups
          group:
        ## Authentication (Main Team) (OIDC)
        oidc:
          ## List of whitelisted OIDC users
          user:
          ## List of whitelisted OIDC groups
          group:
      ## Authentication (CloudFoundry)
      cf:
        enabled: false
        ## (Required) The base API URL of your CF deployment. It will use this information to discover information about the authentication provider.
        # apiUrl: https://api.run.pivotal.io
        ## CA Certificate
        # useCaCert:
        ## Skip SSL validation
        # skipSslValidation:
      ## Authentication (GitHub)
      github:
        enabled: false
        ## Hostname of GitHub Enterprise deployment (No scheme, No trailing slash)
        # host:
        ## CA certificate of GitHub Enterprise deployment
        # useCaCert:
      ## Authentication (GitLab)
      gitlab:
        enabled: false
        ## Hostname of Gitlab Enterprise deployment (Include scheme, No trailing slash)
        # host:
      ## Authentication (LDAP)
      ldap:
        enabled: false
        ## The auth provider name displayed to users on the login page
        # displayName:
        ## (Required) The host and optional port of the LDAP server. If port isn't supplied, it will be guessed based on the TLS configuration. 389 or 636.
        # host:
        ## (Required) Bind DN for searching LDAP users and groups. Typically this is a readOnly user.
        # bindDn:
        ## (Required) Bind Password for the user specified by 'bindDn'
        # bindPw:
        ## Required if LDAP host does not use TLS.
        # insecureNoSsl:
        ## Skip certificate verification
        # insecureSkipVerify:
        ## Start on insecure port, then negotiate TLS
        # startTls:
        ## CA certificate
        # useCaCert:
        ## BaseDN to start the search from. For example 'cn=users,dc=example,dc=com'
        # userSearchBaseDn:
        ## Optional filter to apply when searching the directory. For example '(objectClass=person)'
        # userSearchFilter:
        ## Attribute to match against the inputted username. This will be translated and combined with the other filter as '(<attr>=<username>)'.
        # userSearchUsername:
        ## Can either be: 'sub'  search the whole sub tree or 'one' - only search one level. Defaults to 'sub'.
        # userSearchScope:
        ## A mapping of attributes on the user entry to claims. Defaults to 'uid'.
        # userSearchIdAttr:
        ## A mapping of attributes on the user entry to claims. Defaults to 'mail'.
        # userSearchEmailAttr:
        ## A mapping of attributes on the user entry to claims.
        # userSearchNameAttr:
        ## BaseDN to start the search from. For example 'cn=groups,dc=example,dc=com'
        # groupSearchBaseDn:
        ## Optional filter to apply when searching the directory. For example '(objectClass=posixGroup)'
        # groupSearchFilter:
        ## Can either be: 'sub'  search the whole sub tree or 'one' - only search one level. Defaults to 'sub'.
        # groupSearchScope:
        ## Adds an additional requirement to the filter that an attribute in the group match the user's attribute value. The exact filter being added is: (<groupAttr>=<userAttr value>)
        # groupSearchUserAttr:
        ## Adds an additional requirement to the filter that an attribute in the group match the user's attribute value. The exact filter being added is: (<groupAttr>=<userAttr value>)
        # groupSearchGroupAttr:
        ## The attribute of the group that represents its name.
        # groupSearchNameAttr:
      ## Authentication (OAuth2)
      oauth:
        enabled: false
        ## The auth provider name displayed to users on the login page
        # displayName:
        ## (Required) Authorization URL
        # authUrl:
        ## (Required) Token URL
        # tokenUrl:
        ## UserInfo URL
        # userinfoUrl:
        ## Any additional scopes that need to be requested during authorization
        # scope:
        ## The groups key indicates which claim to use to map external groups to Concourse teams.
        # groupsKey:
        ## CA Certificate
        # useCaCert:
        ## Skip SSL validation
        # skipSslValidation:
      ## Authentication (OIDC)
      oidc:
        enabled: false
        ## The auth provider name displayed to users on the login page
        # displayName:
        ## (Required) An OIDC issuer URL that will be used to discover provider configuration using the .wellKnown/openid-configuration
        # issuer:
        ## Any additional scopes that need to be requested during authorization
        # scope:
        ## The groups key indicates which claim to use to map external groups to Concourse teams.
        # groupsKey:
        ## CA Certificate
        # useCaCert:
        ## Skip SSL validation
        # skipSslValidation:
    tsa:
      ## Minimum level of logs to see.
      logLevel: debug
      ## IP address on which to listen for SSH.
      bindIp: 0.0.0.0
      ## Port on which to listen for SSH.
      bindPort: 2222
      ## Port on which to listen for TSA pprof server.
      # bindDebugPort: 8089
      ## IP address of this TSA, reachable by the ATCs. Used for forwarded worker addresses.
      # peerIp:
      ## Path to private key to use for the SSH server.
      # hostKey:
      ## Path to file containing keys to authorize, in SSH authorized_keys format (one public key per line).
      # authorizedKeys:
      ## Path to file containing keys to authorize, in SSH authorized_keys format (one public key per line).
      # teamAuthorizedKeys:
      ## ATC API endpoints to which workers will be registered.
      # atcUrl:
      ## Path to private key to use when signing tokens in reqests to the ATC during registration.
      # sessionSigningKey:
      ## interval on which to heartbeat workers to the ATC
      # heartbeatInterval: 30s
  worker:
    ## The name to set for the worker during registration. If not specified, the hostname will be used.
    # name:
    ## A tag to set during registration. Can be specified multiple times.
    # tag:
    ## The name of the team that this worker will be assigned to.
    # team:
    ## HTTP proxy endpoint to use for containers.
    # http_proxy:
    ## HTTPS proxy endpoint to use for containers.
    # https_proxy:
    ## Blacklist of addresses to skip the proxy when reaching.
    # no_proxy:
    ## If set, the worker will be immediately removed upon stalling.
    # ephemeral:
    ## Port on which to listen for beacon pprof server.
    # bindDebugPort: 9099
    ## Version of the worker. This is normally baked in to the binary, so this flag is hidden.
    # version:
    ## Directory in which to place container data.
    workDir: /concourse-work-dir
    ## IP address on which to listen for the Garden server.
    # bindIp: 127.0.0.1
    ## Port on which to listen for the Garden server.
    # bindPort: 7777
    ## IP used to reach this worker from the ATC nodes.
    # peerIp:
    ## Minimum level of logs to see.
    # logLevel: info
    tsa:
      ## TSA host to forward the worker through. Can be specified multiple times.
      host: 127.0.0.1:2222
      ## File containing a public key to expect from the TSA.
      # publicKey:
      ## File containing the private key to use when authenticating to the TSA.
      # workerPrivateKey:
    garden:
      ## Minimum level of logs to see.
      # logLevel: info
      ## format of log timestamps
      # timeFormat: unix-epoch
      ## Bind with TCP on the given IP.
      # bindIp:
      ## Bind with TCP on the given port.
      bindPort: 7777
      ## Bind with Unix on the given socket path.
      # bindSocket: /tmp/garden.sock
      ## Bind the debug server on the given IP.
      # debugBindIp:
      ## Bind the debug server to the given port.
      # debugBindPort: 17013
      ## Skip the preparation part of the host that requires root privileges
      # skipSetup:
      ## Directory in which to store container data.
      # depot: /var/run/gdn/depot
      ## Path in which to store properties.
      # propertiesPath:
      ## Path in which to store temporary sockets
      # consoleSocketsPath:
      ## Clean up proccess dirs on first invocation of wait
      # cleanupProcessDirsOnWait:
      ## Disable creation of privileged containers
      # disablePrivilegedContainers:
      ## The lowest numerical subordinate user ID the user is allowed to map
      # uidMapStart: 1
      ## The number of numerical subordinate user IDs the user is allowed to map
      # uidMapLength:
      ## The lowest numerical subordinate group ID the user is allowed to map
      # gidMapStart: 1
      ## The number of numerical subordinate group IDs the user is allowed to map
      # gidMapLength:
      ## Default rootfs to use when not specified on container creation.
      # defaultRootfs:
      ## Default time after which idle containers should expire.
      # defaultGraceTime:
      ## Clean up all the existing containers on startup.
      # destroyContainersOnStartup:
      ## Apparmor profile to use for unprivileged container processes
      # apparmor:
      ## Directory in which to extract packaged assets
      # assetsDir: /var/gdn/assets
      ## Path to the 'dadoo' binary.
      # dadooBin:
      ## Path to the 'nstar' binary.
      # nstarBin:
      ## Path to the 'tar' binary.
      # tarBin:
      ## path to the iptables binary
      # iptablesBin: /sbin/iptables
      ## path to the iptables-restore binary
      # iptablesRestoreBin: /sbin/iptables-restore
      ## Path execute as pid 1 inside each container.
      # initBin:
      ## Path to the runtime plugin binary.
      # runtimePlugin: runc
      ## Extra argument to pass to the runtime plugin. Can be specified multiple times.
      # runtimePluginExtraArg:
      ## Directory on which to store imported rootfs graph data.
      # graph:
      ## Disk usage of the graph dir at which cleanup should trigger, or -1 to disable graph cleanup.
      # graphCleanupThresholdInMegabytes: -1
      ## Image that should never be garbage collected. Can be specified multiple times.
      # persistentImage:
      ## Path to image plugin binary.
      # imagePlugin:
      ## Extra argument to pass to the image plugin to create unprivileged images. Can be specified multiple times.
      # imagePluginExtraArg:
      ## Path to privileged image plugin binary.
      # privilegedImagePlugin:
      ## Extra argument to pass to the image plugin to create privileged images. Can be specified multiple times.
      # privilegedImagePluginExtraArg:
      ## Docker registry API endpoint.
      # dockerRegistry: registry-1.docker.io
      ## Docker registry to allow connecting to even if not secure. Can be specified multiple times.
      # insecureDockerRegistry:
      ## Network range to use for dynamically allocated container subnets.
      # networkPool: 10.254.0.0/22
      ## Allow network access to the host machine.
      # allowHostAccess:
      ## Network ranges to which traffic from containers will be denied. Can be specified multiple times.
      # denyNetwork:
      ## DNS server IP address to use instead of automatically determined servers. Can be specified multiple times.
      # dnsServer:
      ## DNS server IP address to append to the automatically determined servers. Can be specified multiple times.
      # additionalDnsServer:
      ## Per line hosts entries. Can be specified multiple times and will be appended verbatim in order to /etc/hosts
      # additionalHostEntry:
      ## IP address to use to reach container's mapped ports. Autodetected if not specified.
      # externalIp:
      ## Start of the ephemeral port range used for mapped container ports.
      # portPoolStart: 61001
      ## Size of the port pool used for mapped container ports.
      # portPoolSize: 4534
      ## Path in which to store port pool properties.
      # portPoolPropertiesPath:
      ## MTU size for container network interfaces. Defaults to the MTU of the interface used for outbound access by the host. Max allowed value is 1500.
      # mtu:
      ## Path to network plugin binary.
      # networkPlugin:
      ## Extra argument to pass to the network plugin. Can be specified multiple times.
      # networkPluginExtraArg:
      ## Maximum number of microseconds each cpu share assigned to a container allows per quota period
      # cpuQuotaPerShare: 0
      ## Set hard limit for the tcp buf memory, value in bytes
      # tcpMemoryLimit: 0
      ## Default block IO weight assigned to a container
      # defaultContainerBlockioWeight: 0
      ## Maximum number of containers that can be created.
      # maxContainers: 0
      ## Disable swap memory limit
      # disableSwapLimit:
      ## Interval on which to emit metrics.
      # metricsEmissionInterval: 1m
      ## Origin identifier for Dropsonde-emitted metrics.
      # dropsondeOrigin: garden-linux
      ## Destination for Dropsonde-emitted metrics.
      # dropsondeDestination: 127.0.0.1:3457
      ## Path to a containerd socket.
      # containerdSocket:
      ## Use containerd to run processes in containers.
      # useContainerdForProcesses:
      ## Enable proxy DNS server.
      # dnsProxyEnable:
    baggageclaim:
      ## Minimum level of logs to see.
      # logLevel: info
      ## IP address on which to listen for API traffic.
      # bindIp: 127.0.0.1
      ## Port on which to listen for API traffic.
      # bindPort: 7788
      ## Port on which to listen for baggageclaim pprof server.
      # bindDebugPort: 8099
      ## Directory in which to place volume data.
      # volumes:
      ## Driver to use for managing volumes.
      driver: naive
      ## Path to btrfs binary
      # btrfsBin: btrfs
      ## Path to mkfs.btrfs binary
      # mkfsBin: mkfs.btrfs
      ## Path to directory in which to store overlay data
      # overlaysDir:
      ## Interval on which to reap expired volumes.
      # reapInterval: 10s

## Configuration values for Concourse Web components.
##
web:
  ## Override the components name (defaults to web).
  ##
  # nameOverride:

  ## Number of replicas.
  ##
  replicas: 1

  ## Configure resource requests and limits.
  ## ref: https://kubernetes.io/docs/user-guide/compute-resources/
  ##
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"

  ## Configure additional environment variables for the
  ## web containers.
  # env:
  #   - name: CONCOURSE_LOG_LEVEL
  #     value: "debug"
  #   - name: CONCOURSE_TSA_LOG_LEVEL
  #     value: "debug"

  ## Additional affinities to add to the web pods.
  ##
  # additionalAffinities:
  #   nodeAffinity:
  #     preferredDuringSchedulingIgnoredDuringExecution:
  #       - weight: 50
  #         preference:
  #           matchExpressions:
  #             - key: spot
  #               operator: NotIn
  #               values:
  #                 - "true"

  ## Annotations for the web nodes.
  ## Ref: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/
  annotations: {}
  # annotations:
  #   key1: "value1"
  #   key2: "value2"

  ## Node selector for web nodes.
  nodeSelector: {}

  ## Tolerations for the web nodes.
  ## Ref: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []
  # tolerations:
  #  - key: "toleration=key"
  #    operator: "Equal"
  #    value: "value"
  #    effect: "NoSchedule"

  ## Service configuration.
  ## ref: https://kubernetes.io/docs/user-guide/services/
  ##
  service:
    ## For minikube, set this to ClusterIP, elsewhere use LoadBalancer or NodePort
    ## ref: https://kubernetes.io/docs/user-guide/services/#publishing-services---service-types
    ##
    type: ClusterIP

    ## When using web.service.type: LoadBalancer, sets the user-specified load balancer IP
    # loadBalancerIP: 172.217.1.174

    ## Annotations to be added to the web service.
    ##
    # annotations:
    #   prometheus.io/probe: "true"
    #   prometheus.io/probe_path: "/"
    #
    #   ## When using web.service.type: LoadBalancer, enable HTTPS with an ACM cert
    #   service.beta.kubernetes.io/aws-load-balancer-ssl-cert: "arn:aws:acm:eu-west-1:123456789:certificate/abc123-abc123-abc123-abc123"
    #   service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "http"
    #   service.beta.kubernetes.io/aws-load-balancer-backend-port: "atc"
    #   service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "443"
    #
    # ## When using web.service.type: LoadBalancer, whitelist the load balancer to particular IPs
    # loadBalancerSourceRanges:
    #   - 192.168.1.10/32

  # When using web.service.type: NodePort, sets the nodePort for atc
  #  atcNodePort: 30150
  #
  # When using web.service.type: NodePort, sets the nodePort for tsa
  #  tsaNodePort: 30151

  ## Ingress configuration.
  ## ref: https://kubernetes.io/docs/user-guide/ingress/
  ##
  ingress:
    ## Enable Ingress.
    ##
    enabled: false

    ## Annotations to be added to the web ingress.
    ##
    # annotations:
    #   kubernetes.io/ingress.class: nginx
    #   kubernetes.io/tls-acme: 'true'

    ## Hostnames.
    ## Must be provided if Ingress is enabled.
    ##
    # hosts:
    #   - concourse.domain.com

    ## TLS configuration.
    ## Secrets must be manually created in the namespace.
    ##
    # tls:
    #   - secretName: concourse-web-tls
    #     hosts:
    #       - concourse.domain.com
    #
    #

## Configuration values for Concourse Worker components.
##
worker:
  ## Override the components name (defaults to worker).
  ##
  # nameOverride:

  ## Number of replicas.
  ##
  replicas: 2

  ## Minimum number of workers available after an eviction
  ## ref: https://kubernetes.io/docs/admin/disruptions/
  ##
  minAvailable: 1

  ## Configure resource requests and limits.
  ## ref: https://kubernetes.io/docs/user-guide/compute-resources/
  ##
  resources:
    requests:
      cpu: "100m"
      memory: "512Mi"

  ## Configure additional environment variables for the
  ## worker container(s)
  # env:
  #   - name: http_proxy
  #     value: "http://proxy.your-domain.com:3128"
  #   - name: https_proxy
  #     value: "http://proxy.your-domain.com:3128"
  #   - name: no_proxy
  #     value: "your-domain.com"
  #   - name: CONCOURSE_GARDEN_DNS_SERVER
  #     value: "8.8.8.8"
  #   - name: CONCOURSE_GARDEN_DNS_PROXY_ENABLE
  #     value: "true"
  #   - name: CONCOURSE_GARDEN_ALLOW_HOST_ACCESS
  #     value: "true"


  ## Configure additional volumeMounts for the
  ## worker container(s)
  # additionalVolumeMounts:
  #   - name: concourse-baggageclaim
  #     mountPath: /baggageclaim

  ## Annotations to be added to the worker pods.
  ##
  # annotations:
  #   iam.amazonaws.com/role: arn:aws:iam::123456789012:role/concourse
  #

  ## Node selector for the worker nodes.
  ## Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodeselector
  nodeSelector: {}
  # nodeSelector: {type: concourse}

  ## Additional affinities to add to the worker pods.
  ## Useful if you prefer to run workers on non-spot instances, for example
  ##
  # additionalAffinities:
  #   nodeAffinity:
  #     preferredDuringSchedulingIgnoredDuringExecution:
  #       - weight: 50
  #         preference:
  #           matchExpressions:
  #             - key: spot
  #               operator: NotIn
  #               values:
  #                 - "true"

  ## Configure additional volumes for the
  ## worker container(s)
  # additionalVolumes:
  #   - name: concourse-baggageclaim
  #     hostPath:
  #       path: /dev/nvme0n1
  #       type: BlockDevice
  #
  # As a special exception, this allows taking over the `concourse-work-dir`
  # volume (from the default emptyDir) if `persistence.enabled` is false:
  #
  # additionalVolumes:
  #   - name: concourse-work-dir
  #     hostPath:
  #       path: /mnt/locally-mounted-fast-disk/concourse
  #       type: DirectoryOrCreate

  ## Whether the workers should be forced to run on separate nodes.
  ## This is accomplished by setting their AntiAffinity with requiredDuringSchedulingIgnoredDuringExecution as opposed to preferred
  ## Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#inter-pod-affinity-and-anti-affinity-beta-feature
  hardAntiAffinity: false

  ## Tolerations for the worker nodes.
  ## Ref: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/
  tolerations: []
  # tolerations:
  #  - key: "toleration=key"
  #    operator: "Equal"
  #    value: "value"
  #    effect: "NoSchedule"

  ## Time to allow the pod to terminate before being forcefully terminated. This should provide time for
  ## the worker to retire, i.e. drain its tasks. See https://concourse-ci.org/worker-internals.html for worker
  ## lifecycle semantics.
  terminationGracePeriodSeconds: 60

  ## If any of the strings are found in logs, the worker's livenessProbe will fail and trigger a pod restart.
  ## Specify one string per line, exact matching is used.
  ##
  fatalErrors: |-
    guardian.api.garden-server.create.failed
    baggageclaim.api.volume-server.create-volume-async.failed-to-create

  ## Strategy for StatefulSet updates (requires Kubernetes 1.6+)
  ## Ref: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset
  ##
  updateStrategy: RollingUpdate

  ## Pod Management strategy (requires Kubernetes 1.7+)
  ## Ref: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#pod-management-policies
  ##
  ## "OrderedReady" is default. "Parallel" means worker pods will launch or terminate
  ## in parallel.
  podManagementPolicy: Parallel

## Persistent Volume Storage configuration.
## ref: https://kubernetes.io/docs/user-guide/persistent-volumes
##
persistence:
  ## Enable persistence using Persistent Volume Claims.
  ##
  enabled: true

  ## Worker Persistence configuration.
  ##
  worker:
    ## concourse data Persistent Volume Storage Class
    ## If defined, storageClassName: <storageClass>
    ## If set to "-", storageClassName: "", which disables dynamic provisioning
    ## If undefined (the default) or set to null, no storageClassName spec is
    ##   set, choosing the default provisioner.  (gp2 on AWS, standard on
    ##   GKE, AWS & OpenStack)
    ##
    # storageClass: "-"

    ## Persistent Volume Access Mode.
    ##
    accessMode: ReadWriteOnce

    ## Persistent Volume Storage Size.
    ##
    size: 20Gi

## Configuration values for the postgresql dependency.
## ref: https://github.com/kubernetes/charts/blob/master/stable/postgresql/README.md
##
postgresql:

  ## Use the PostgreSQL chart dependency.
  ## Set to false if bringing your own PostgreSQL, and set secret value postgresql-uri.
  ##
  enabled: true

  ### PostgreSQL User to create.
  ##
  postgresUser: concourse

  ## PostgreSQL Password for the new user.
  ## If not set, a random 10 characters password will be used.
  ##
  postgresPassword: concourse

  ## PostgreSQL Database to create.
  ##
  postgresDatabase: concourse

  ## Persistent Volume Storage configuration.
  ## ref: https://kubernetes.io/docs/user-guide/persistent-volumes
  ##
  persistence:
    ## Enable PostgreSQL persistence using Persistent Volume Claims.
    ##
    enabled: true
    ## concourse data Persistent Volume Storage Class
    ## If defined, storageClassName: <storageClass>
    ## If set to "-", storageClassName: "", which disables dynamic provisioning
    ## If undefined (the default) or set to null, no storageClassName spec is
    ##   set, choosing the default provisioner.  (gp2 on AWS, standard on
    ##   GKE, AWS & OpenStack)
    ##
    # storageClass: "-"
    ## Persistent Volume Access Mode.
    ##
    accessMode: ReadWriteOnce
    ## Persistent Volume Storage Size.
    ##
    size: 8Gi

## For RBAC support:
rbac:
  # true here enables creation of rbac resources
  create: true

  # rbac version
  apiVersion: v1beta1

  ## The name of the service account to use for web pods if rbac.create is false
  ##
  webServiceAccountName: default

  ## The name of the service account to use for worker pods if rbac.create is false
  ##
  workerServiceAccountName: default

## For managing secrets using Helm
##
secrets:

  ## List of username:bcrypted_password combinations for all your local concourse users.
  localUsers: "test:$2a$10$sDB6AsH2HheOWHILrnHVJOCZq/GYtUYE02ypJJTQBmWJNivYNhP3y"
  ## Create the secret resource from the following values. Set this to
  ## false to manage these secrets outside Helm.
  ##
  create: true

  ## Concourse Host Keys.
  ## ref: https://concourse-ci.org/install.html#generating-keys
  ##
  hostKey: |-
    -----BEGIN RSA PRIVATE KEY-----
    MIIEogIBAAKCAQEA2AUPXxuiDC/qrBWjIdT5fvNcMlMEYpR3X4SLQIgLC1ULDsCO
    fleKZ+Wi4RzwbkUKiKmJm5GeyNVVCDdfvdD1Sd1+5faqmp2/OQBzLS7o8NY/btMw
    8h9lx4KVJaJJ1EM1EiyGY41Nx591KP14pBfr0/NdOIrDu2JvF6e7CHEbrzkN57kb
    BVQkaIMaS01Rw/5Oe68GFalli2ii8L8dNWVVzquBh5PwVWimvTgwv3TYG2TH8L1V
    V7n+/zRRpkjMl2+PUouGqD+Bp+4wF+hp4AW5v24CqjtLJEMv4IEJv2FRfrOauBIZ
    XjAS1SSg9VaTOS3iwxaYrv8uG1XfMFHICvkEPQIDAQABAoIBAG87W8jrX6vK2Jm3
    ooJ/OeFmymiXWsCwFi+2/kVCR/2T0tfLyxO/W+NX2WD1F9CP+HaaZeMXPp3HS7up
    V8FT4ZohVYBwXTS0WYyucKApcYThrVQRpzhldnEfClGQmVeVK7Sp/KEyV4Sc1SVA
    L2i/cI142N2Ohm7spquVkLcuFsVINzZ0fXCv25dTqbkEgjTJzNdBzyFXvc4z0Mt9
    gW14M7mz+YKYOfsCxIEm438fC9b16C96yIFBdN+/jaP8pmb2RoIE2D0F8bj5K1hR
    YyGFKMOU4e6cYq59iWfubKuu2WNJEBk/5aO7x7Xu2S0k8wIYlwxFuu4LfR2Kvizu
    +mFVf3kCgYEA9e0+40tJGpOPM8hAB3DwXjYc8lCuyYf3z30T3RqVNCUVSWnlaj/s
    3ENi6+Ng3u+Zs8cR2CFou+jAClTyWLuSnI9yACD0eyW9n4bzYMUbgdC6vneLjpzx
    wWR9Xv5RmZVly7xWuqcgEeEf8RNcYI3oXby0laF3EObvuAx/4ETIkFcCgYEA4N42
    w1UEWGopWBIIXYHkEPHQuF0SxR2CZyh9ExTeSxFphyibkcHRjDW+t91ZLnSm5k1N
    TOdYuc0ApBV3U+TexeFvDI94L/Oze6Ht5MatRQz8kRwMFGJL3TrpbgTmWdfG05Ad
    oiScJzwY16oJXnKusxik7V+gCCNNE0/2UuMnY4sCgYAEf82pvOPef5qcGOrK+A79
    ukG3UTCRcVJgUmp9nhHivVbxW+WdlwPPV9BEfol0KrAGMPsrmBjhbzWsOregVfYt
    tRYh2HiAlEUu2Po06AZDzrzL5UYBWu+1WRBOH5sAk1IkcxKnIY2dph++elszTQVW
    SbCIGEckYQU7ucbRJJECywKBgBb4vHFx8vKxTa3wkagzx7+vZFohL/SxEgxFx5k2
    bYsPqU8kZ9gZC7YeG3CfDShAxHgMd5QeoiLA/YrFop4QaG2gnP6UfXuwkqpTnYDc
    hwDh1b9hNR6z9/oOtaAGoh2VfHtKYqyYvtcHPaZyeWiLoKstHlQdi7SpHouVhJ1t
    FS4HAoGAGy+56+zvdROjJy9A2Mn/4BvWrsu4RSQILBJ6Hb4TpF46p2fn0rwqyhOj
    Occs+xkdEsI9w5phXzIEeOq2LqvWHDPxtdLpxOrrmx4AftAWdM8S1+OqTpzHihK1
    y1ZOrWfvON+XjWFFAEej/CpQZkNUkTzjTtSC0dnfAveZlasQHdI=
    -----END RSA PRIVATE KEY-----

  hostKeyPub: |-
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDYBQ9fG6IML+qsFaMh1Pl+81wyUwRilHdfhItAiAsLVQsOwI5+V4pn5aLhHPBuRQqIqYmbkZ7I1VUIN1+90PVJ3X7l9qqanb85AHMtLujw1j9u0zDyH2XHgpUloknUQzUSLIZjjU3Hn3Uo/XikF+vT8104isO7Ym8Xp7sIcRuvOQ3nuRsFVCRogxpLTVHD/k57rwYVqWWLaKLwvx01ZVXOq4GHk/BVaKa9ODC/dNgbZMfwvVVXuf7/NFGmSMyXb49Si4aoP4Gn7jAX6GngBbm/bgKqO0skQy/ggQm/YVF+s5q4EhleMBLVJKD1VpM5LeLDFpiu/y4bVd8wUcgK+QQ9 Concourse

  ## Concourse Session Signing Keys.
  ## ref: https://concourse-ci.org/install.html#generating-keys
  ##
  sessionSigningKey: |-
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEAwLql/rUIaI+PX7Tl3FWcTee4sQf8/daakALXx955tPwkhqlY
    e4T2V84p/ylFvNWpM4vfcMYKfMY0JLKgAgBvJhCytSkDBhTBoWmN6yE0AB11P9En
    lIZRBWNYqaC2cSge2ZD8qOSnwfFhnQAW8+7pE+ElJAVh7dtdF3A478H50lIigq8I
    zMWp2EGJpFC7/Uu36oIL/03MNGCmrH1jvtTuJiAMQUZYyL1ReBkvvHOzw9i4HXPy
    SMVtcllm4NBs2aVPtwhr2kwSkLt8t1bPdRn6OIyEAw5WktzAKaiZnkTvj6g3xzdp
    zKcrdlBr9aznlNvoSinBUfvtwyFmvFN1HHbA9wIDAQABAoIBAE7G/DrUfI9gvtX7
    90jMpYsigFe8UCjho2PiBZlo0o6r0bJJXiV+/8J8PqZRlHPPUc4EClzqVjcSPRYS
    /VxUGRqSELoD/Xxq14rGvn+xnrO9VsOzFl6bWFq/dOpBCtHN+G4t2VifvgKES8YE
    11z19sdta+UBXjn/RFnkQSGfRCI3QqTaYvjxevt0uWlyPmqkFPQQw8bvHIXzoB+B
    rzeiMa++nMvbX5pAH9XA0BvhyuH3fHidTUwiVBpkMcpLWtjP0A0JTsecDdbinDDq
    un2EIo8zMWRwKQN/JnUxsi8AUEigBTCUqeDgREXtW62uvFkSpcVMXwmVityLYIVy
    qnVLUCECgYEA6IwXkP1qnSfcNeoVI/ypDuz1/kdqcjSPhLYe+jdiLLoFkMW9AlDm
    lzwNaWlTFD9ygo+NjJCo63/A8HCm55sajws5hZ6r20vdZcKFMk9h0qF5oVA7lkQ2
    gvG2WaznuU7KkqhfP+pXhiLgZKoJkst/+g7r6uHpredwDY6hxeBK4vsCgYEA1CqH
    8ywC5qUo/36kQg/TU2adN/YEHdJAAbU23EVrGQSVmnXW08H2NLFk0tsxrwoNnbgp
    PIk2J7BimbJvbND17ibr4GAklDTsR8aJkDl+0JgNCAK9N07qVt1s7FXzhg95jUL9
    EQW55z60GAJpecqNwA4Jsa8P852N0355Obp92TUCgYBkOBvf7JcJ66fHxH4f6D+j
    oxPQ5k5Fsck4VJS9GSlCRVkor09ptBvsiYDuMOoRC9b51YwXTDDAbWplNOd5YSrt
    AtVjdKJz/BoKRO7KY9Owxs54au+DLxqfDDSeKRokjoRW+CE0lnXp5RX3zCAcF3+r
    8MpTi9D9lYSBEzs84BDmCQKBgQCMcH6/K3HcJJVn0fd+tyUGftUw9sswxjySJNbk
    pZrH263/qWMDls+Xf5kire9MU1ZCAWZiaN0NFoed/2wcVpGEDAV0548u/30r4bKr
    YjOcdhmiJNYFJ1qdF0MDib2CDvpB1IbZXrX46RujDO2urbJ435HxKNVhR/had8xc
    tyKYxQKBgCVDhN0MhnlUQJVZfX42APmF4gQg0r3sfL/NGXjEjMIKKFe5a88eZVHr
    L8x1+dp0q7czC8a/l1DUuiwDKl8OEpxLsGCq/J/wAfrSMPifu6EUlbUwlJOPdgha
    +p/KFAelHXJ2w/8yackAcarh35VP7ixhuvxswHNdgvfsBTFcjn30
    -----END RSA PRIVATE KEY-----

  ## Concourse Worker Keys.
  ## ref: https://concourse-ci.org/install.html#generating-keys
  ##
  workerKey: |-
    -----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEAuPehUmBXAQCoA7TLAQCYhf+vzcZVyj+VGXnMhLHnWLk7dRjo
    CU8GgNamdS5h7G3ywxOvKA3YjOLr8XyOMLS4c+e8N7tIzlMWdiXhe0lcBH9Z1ai5
    +Bof3/BlDUBksiKdc1A+QcfX6tDwMkOO5re1H4vOK3H/Cype58wCB03HYNgb05ED
    fW1Bj2qvz29VtmyjwEMuDs100iMqwCfPUx9oxXmmX8sUBRmw/Y1Rx/8pdKIjKw3m
    kWIHHBOSCPimO1qC47Aa8v/UH9hERCykyuFHiBiKlnIvZWm9bYvhsRTz4gt5KzRY
    6OI0oVeHlLOHDSK48Da8VWij15lOqO2Nx6WssQIDAQABAoIBADET22UNFOi6MNpS
    5S5N5ypezlnOD0NLnZcV3zMyNQ0wkNsgEakuo64Zxi7/cJIYFjq2hVoeWl//cdUw
    VFYODYcLbMBo3AeKukH9CRf6PgUfeUmcrENtQxnbIiTi+hTd5GMNXod7rAmtCJ59
    mHQVOGS3ZqvWYnKm+mmMktk3RPinynX/A4y3WHPacuAS58HM09Ck43WcHMxbGpsL
    /gZpICyFYZ2DviM+AHyWGcmw7LJrpC0QHo6+BAFMs4xlUecNgVIFUpfOoAcfsdtG
    K9j4AbuZ47iFisbay+1pyg/7O5eRTdGVQRtc7PBMOjea5jGsfmlDmdn1ZS50ykun
    ANfoQ5UCgYEA9Ak73PRy9nLlRkt4OBCF/4fwThUCMedsnWaVjQBMJYim4FB2ivF5
    cKdWt3y/RZI85KKYu0EXhLEoSIEAfz057R8t3QdVK4tZx6B47UFjBjCYeVMtwHDQ
    prxQiOPHIHCplBNFuGzA5VXL9gQLRD+ek0uOy2GJJ0Wu1xyeouI+SW8CgYEAwgkO
    TOtOogqmcAALjWgeeQiZetflSKbJlpQNhmCPAMm0SFI8eF4SpRXLzd41VC2mLIwT
    L3tjc7/8ocXoElFM4L0fo9Lx/SHFH4JEn5FT0PXPmvsF2JRhsXJFLJSihxF/91Xs
    2aBcQILPFzLcrI6OFUakNwGTU/CIxpkzRvQrG98CgYEAzNVnUuo4CNadzagRK3Xr
    E3Yl5VRK+FpY17FAfA6w25xc/dFr/un61e0Po4no/ltmEz7LVfmn5O/ScTEemq5o
    jbjrBShfe+JGpIH0nqiQlqR5hvSjZXEMIbfVHWGbRYZrQGgA0HEwZA7k2QXB8zI3
    R0lXfSzMM5OQ0uwp12xxfa8CgYBHILq1R6zTicPpWprhg0FobNaWSX4rW7iaEjvC
    /rJtP4Nu33Z7SUDcc1j6ZnJ2ISXBPrfpt/mE/OPHCZ1A2bysxadLjpBWkoKIQmCV
    fdiTyQgJb+t8sSf+vDzPUs0hZjDaogzo2ff3TfxMLMDoIHnFItgfsdwn8QyygIZj
    hC4pUQKBgQDqsxnkI6yXFE5gshnW7H8zqKNlzKd/dZEL6e+lRz4R3UY/KcEkRAfq
    Yi3cwo9fE3U3kSmpl5MQwUjWm/BZ7JyueoY/4ndwaFPgc34IKsgJ0wau9pZiQAB1
    DxpOSF+BR71Jx3sxvIdCODNTtm645j5yrZVnJAuMPofo5XFmunDoJA==
    -----END RSA PRIVATE KEY-----

  workerKeyPub: |-
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC496FSYFcBAKgDtMsBAJiF/6/NxlXKP5UZecyEsedYuTt1GOgJTwaA1qZ1LmHsbfLDE68oDdiM4uvxfI4wtLhz57w3u0jOUxZ2JeF7SVwEf1nVqLn4Gh/f8GUNQGSyIp1zUD5Bx9fq0PAyQ47mt7Ufi84rcf8LKl7nzAIHTcdg2BvTkQN9bUGPaq/Pb1W2bKPAQy4OzXTSIyrAJ89TH2jFeaZfyxQFGbD9jVHH/yl0oiMrDeaRYgccE5II+KY7WoLjsBry/9Qf2ERELKTK4UeIGIqWci9lab1ti+GxFPPiC3krNFjo4jShV4eUs4cNIrjwNrxVaKPXmU6o7Y3Hpayx Concourse

  ## Secrets for DB access
  # postgresUser:
  # postgresPassword:
  # postgresCaCert:
  # postgresClientCert:
  # postgresClientKey:

  ## Secrets for DB encryption
  ##
  # encryptionKey:
  # oldEncryptionKey:

  ## Secrets for SSM AWS access
  # awsSsmAccessKey:
  # awsSsmSecretKey:
  # awsSsmSessionToken:

  ## Secrets for Secrets Manager AWS access
  # awsSecretsmanagerAccessKey:
  # awsSecretsmanagerSecretKey:
  # awsSecretsmanagerSessionToken:

  ## Secrets for CF OAuth
  # cfClientId:
  # cfClientSecret:
  # cfCaCert: |-

  ## Secrets for GitHub OAuth.
  ##
  # githubClientId:
  # githubClientSecret:
  # githubCaCert: |-

  ## Secrets for GitLab OAuth.
  ##
  # gitlabClientId:
  # gitlabClientSecret:

  ## Secrets for LDAP Auth.
  ##
  # ldapCaCert: |-

  ## Secrets for generic OAuth.
  ##
  # oauthClientId:
  # oauthClientSecret:
  # oauthCaCert: |-

  ## Secrets for oidc OAuth.
  ##
  # oidcClientId:
  # oidcClientSecret:
  # oidcCaCert: |-

  ## Secrets for using Hashcorp Vault as a credential manager.
  ##
  ## if the Vault server is using a self-signed certificate, provide the CA public key.
  ## the value will be written to /concourse-vault/ca.cert
  ##
  # vaultCaCert: |-

  ## initial periodic token issued for concourse
  ## ref: https://www.vaultproject.io/docs/concepts/tokens.html#periodic-tokens
  ##
  # vaultClientToken:

  ## vault authentication parameters
  ## Paramter to pass when logging in via the backend
  ## Required for "approle" authenication method
  ## e.g. "role_id=x,secret_id=x"
  ## ref: https://concourse-ci.org/creds.html#vault-auth-param=NAME=VALUE
  ##
  # vaultAuthParam:

  ## provide the client certificate for authenticating with the [TLS](https://www.vaultproject.io/docs/auth/cert.html) backend
  ## the value will be written to /concourse-vault/client.cert
  ## make sure to also set credentialManager.vault.authBackend to `cert`
  ##
  # vaultClientCert: |-

  ## provide the client key for authenticating with the [TLS](https://www.vaultproject.io/docs/auth/cert.html) backend
  ## the value will be written to /concourse-vault/client.key
  ## make sure to also set credentialManager.vault.authBackend to `cert`
  ##
  # vaultClientKey: |-

  ## If influxdb metrics are enabled and authentication is required,
  ## provide a password here to authenticate with the influxdb server configured.
  ##
  # influxdbPassword:

  ## SSL certificate used to verify the Syslog server for draining build logs.
  # syslogCaCert: |-''')
	s.send('nohup minikube dashboard &')
	s.send_until('kubectl get all --all-namespaces | grep tiller | grep pod | grep Running | wc -l','1')
	s.send('helm install stable/concourse -f custom_values.yaml')
	name = s.send_and_get_output('helm list -q')
	s.send_until('kubectl get pod | grep -v Running | grep -v NAME | wc -l','0')
	s.send('nohup kubectl port-forward service/' + name + '-web 8080:8080 &')
	s.pause_point('deployed on 127.0.0.1:8080?')
