import random

def do_istio(s, version):
	s.send('rm -rf ~/minikube_tmp/istiotmp')
	s.send('mkdir -p ~/minikube_tmp/istiotmp')
	s.send('cd ~/minikube_tmp/istiotmp')
	OS = s.send_and_get_output('uname')
	s.send('git clone https://github.com/istioinaction/book-source-code')
	if OS == 'Linux':
		s.send('wget -qO- https://github.com/istio/istio/releases/download/' + version + '/istio-' + version + '-linux.tar.gz | tar -zxvf -')
	elif OS == 'Darwin':
		s.send('wget -qO- https://github.com/istio/istio/releases/download/' + version + '/istio-' + version + '-osx.tar.gz | tar -zxvf -')
	s.send('cd istio-' + version)
	s.send('./bin/istioctl version')
	s.send('PATH=$(pwd)/bin:${PATH}')
	# Errors at end here (no matter which version of istio?)
	s.send('kubectl create -f install/kubernetes/istio-demo.yaml || true')
	s.send_until('kubectl get pod -n istio-system | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0', cadence=20)
	s.send("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl -n istio-system --command -- curl -v 'http://istio-pilot.istio-system:8080/v1/registration'")


# Istio in Action book
def do_istioinaction(s):
	s.send('cd ../book-source-code')
	# Deploy first app in service mesh.
	#p.53
	s.send('kubectl create namespace istioinaction',note='Create istioinaction namespace')
	s.send('kubectl config set-context $(kubectl config current-context) --namespace=istioinaction',note='Update kubectl context')
	#p.56
	s.send('kubectl create -f <(istioctl kube-inject -f install/catalog-service/catalog-all.yaml)',note='Deploy catalog app')
	s.send_until('kubectl get pod | grep catalog | wc -l','1')
	s.send_until('kubectl get pod | grep catalog | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0', cadence=20)
	s.send('sleep 60')
	s.send("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl --command -- sh -c 'curl -s catalog:8080/api/catalog'",note='Now catalog is up, curl it')
	#p.57
	s.send('kubectl create -f <(istioctl kube-inject -f install/apigateway-service/apigateway-all.yaml)',note='Deploy API gateway service')
	s.send_until('kubectl get pod | grep apigateway | wc -l','1')
	s.send_until('kubectl get pod | grep apigateway | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0', cadence=20)
	s.send('sleep 60')
	s.send("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl --command -- sh -c 'curl -s apigateway:8080/api/products'",note='curl apigateway')

	# 2.4 Exploring... resilience observability and traffic control
	# Ingress gateway in istio-system
	#p.58
	s.send('kubectl config set-context $(kubectl config current-context) --namespace=istio-system',note='Change to istio system namespace')
	s.send('kubectl create -f chapter-files/chapter2/ingress-gateway.yaml',note='Create ingress gateway')
	URL = s.send_and_get_output("""$(minikube ip):$(kubectl get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')""",note='Construct ingress gateway URL')
	s.send('curl ' + URL + '/api/products',note='Curl for products')
	#p.59
	s.send("istioctl proxy-config routes $(kubectl get pod | grep ingress | cut -d ' ' -f 1)",note='Get routes from proxy config')
	s.send('kubectl config set-context $(kubectl config current-context) --namespace=istioinaction',note='Back to istioinaction')
	s.send('kubectl get gateway',note='Show gateway')
	s.send('kubectl get virtualservice',note='Get virtual service')

	# 2.4.1 Istio observability
	# Generate some traffic
	for _ in []*5:
		s.send('do curl ' + URL + '/api/products; sleep .5; done')
	# Grafana
	s.send('sleep 60')
	# p.60
	GRAFANA = s.send_and_get_output('''kubectl -n istio-system get pod | grep -i running | grep grafana | cut -d ' ' -f 1''',note='Get grafana pod')
	random_port = str(random.randrange(49152,65535))
	s.send('''kubectl port-forward -n istio-system "''' + GRAFANA + '''" ''' + random_port + ''':3000 &''',note='Forward port from grafana:3000 to a random port')
	#s.pause_point('now go to localhost:' + random_port)
	# Jaeger tracing
	s.send('sleep 60')
	# p.63
	TRACING = s.send_and_get_output('''kubectl -n istio-system get pod | grep istio-tracing | cut -d ' ' -f 1''',note='Get tracing pod')
	random_port = str(random.randrange(49152,65535))
	s.send('''kubectl port-forward -n istio-system "''' + TRACING + '''" ''' + random_port + ''':16686 &''',note='Forward port from tracing service:16686 to random port')
	# Generate some traffic
	for _ in []*5:
		s.send('do curl ' + URL + '/api/products; sleep .5; done')
	#s.pause_point('now go to localhost:' + random_port)
	# 2.4.2 Istio for resiliency
	# Generate a failure
	# p.67
	s.send('curl ' + URL + '/api/products -H "failure-percentage: 100"',note='Induce a failure in lookup')

	# 2.4.3 Istio for traffic routing
	# p.68
	s.send('''kubectl create -f chapter-files/chapter2/catalog-virtualservice.yaml''',note='Set up ingress gateway')
	# Generate traffic
	for _ in []*10:
		s.send('curl ' + URL + '/api/products -H "failure-percentage: 50"')
	# p.70
	s.send('kubectl create -f <(istioctl kube-inject -f ./install/catalog-v2-service/catalog-v2-deployment.yaml)',note='Create an istio-d catalog v2')
	s.send('kubectl create -f chapter-files/chapter2/catalog-destinationrule.yaml',note='Set up destination rule')
	# p.71
	s.send('kubectl apply -f chapter-files/chapter2/catalog-virtualservice-all-v1.yaml',note='Set up virtualservice')
	# v1 responses only now
	for _ in []*5:
		s.send('curl ' + URL + '/api/products')
	# p.72
	s.send('kubectl apply -f chapter-files/chapter2/catalog-virtualservice-dark-v2.yaml',note='Create version 2 of the service, only available through dark launch')
	for _ in []*5:
		s.send('curl ' + URL + '/api/products')
	# Call 'dark launch'
	s.send('curl ' + URL + '/api/products -H "x-dark-launch: v2"',note='Get dark launch, expect bunch of json')
	s.send('kill %1')
	s.send('kill %2')

	# CHAPTER 3
	# 3.3 Envoy in action
	# p.87
	s.send('''eval $(minikube docker-env)''',note='Move to docker environment and then pull images')
	s.send('docker ps')
	s.send('docker pull istioinaction/envoy:v1.7.0')
	s.send('docker pull tutum/curl')
	s.send('docker pull citizenstig/httpbin')
	# p.88
	TODO annotate from here.
	s.send('docker run -d --name httpbin citizenstig/httpbin')
	s.send('docker run -it --rm --link httpbin tutum/curl curl -X GET http://httpbin:8000/headers',note='Look at httpbin:8000 headers')
	s.send('docker run -it --rm istioinaction/envoy:v1.7.0 envoy --help',note='Show envoy help')
	s.send('docker run -it --rm istioinaction/envoy:v1.7.0 envoy || true',note='Run envoy with no config (will fail)')
	s.send('docker run -i --rm --entrypoint "cat" istioinaction/envoy:v1.7.0 /etc/envoy/simple.yaml',note='Run sith a simple config (cat-ed above)')
	s.send('docker run -d --name proxy --link httpbin istioinaction/envoy:v1.7.0 envoy -c /etc/envoy/simple.yaml',note='Run envoy with a simple proxy config')
	s.send('docker logs proxy',note='Look at envoy logs')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15001/headers',note='Look at proxy:15001 headers')
	s.send('docker rm -f proxy',note='Delete proxy')
	s.send('docker run -i --rm --link httpbin --entrypoint diff istioinaction/envoy:v1.7.0 /etc/envoy/simple.yaml /etc/envoy/simple_change_timeout.yaml',note='Show diff between last config and new one')
	s.send('docker run -d --name proxy --link httpbin istioinaction/envoy:v1.7.0 envoy -c /etc/envoy/simple_change_timeout.yaml',note='Run again, but change timeout (different config)')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15001/headers',note='Get headers')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/stats',note='Get stats')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/stats | grep retry',note='Too much crap - now grep for retry')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/',note='Get list of endpoints - explore!')
	s.send('docker rm -f proxy',note='Delete proxy')
	s.send('docker run -d --name proxy --link httpbin istioinaction/envoy:v1.7.0 envoy -c /etc/envoy/simple_retry.yaml',note='un again, but change retry policy')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15001/status/500',note='create a 500 error by calling /status/500')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/stats | grep retry',note='what happened?')
	# CHAPTER 4
	INGRESS_POD = s.send_and_get_output('kubectl get pod -n istio-system | grep ingressgateway | cut -d ' ' -f 1',note='Get ingress gateway pod')
	s.send('kubectl -n istio-system exec ' + INGRESS_POD + ' ps aux',note='Show processes running within gateway pod')
	s.send('kubectl create -f chapter-files/chapter4/coolstore-gw.yaml',note='Create coolstore gateway')
	s.send('istioctl proxy-config listener ' + INGRESS_POD + ' -n istio-system',note='Expect to see a listener on 0.0.0.0:80 of type HTTP')
	s.send('istioctl proxy-config route ' + INGRESS_POD + ' -n istio-system',note='View the route in json. Start by matching everything to 404')
#[
# {
# "name": "http.80",
# "virtualHosts": [
# {
# "name": "blackhole:80",
# "domains": [
# "*"
# ],
# "routes": [
# {
# "match": {
# "prefix": "/"
# },
# "directResponse": {
# "status": 404
# },
# "perFilterConfig": {
# "mixer": {}
# }
# }
# ]
# }
# ],
# "validateClusters": false
# }
#]
	# Pod running on the custom gateway should be listening on an address that is exposed outside the cluster.
	# For example on local minikube, we're listening on a NodePort. If on GKE you'll want to use a loadblaancer that
	# gets an externally routable IP address.
	# In Istio, A VirtualService resource maps a FQDN, version and other routing properties to services.
	# VirtualService contains the preferred gateway, referenced by gateways: in the yaml spec.
	# Istio Gateway handles the L4 and L5 concerns while Gateway VirtualService handles the L7 concerns.
	# L4 concerns: Ports
	# L5 concerns: Connecting to (?)
	# L7 concerns: HTTP headers
	s.send('kubectl create -f chapter-files/chapter4/coolstore-vs.yaml',note='create the VirtualService')
	# Check the apigateway and catalog pods are there.
	s.send('kubectl get pod',note='should see two pods ready')
	s.send('kubectl get gateway',note='check gateway exists')
	s.send('kubectl get virtualservice',note='check virtualservice exists')
	HTTP_HOST = s.send_and_get_output('minikube ip')
	HTTP_PORT = s.send_and_get_output("""kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}'""")
	URL = HTTP_HOST + ':' + HTTP_PORT
	s.send('curl ' + URL + '/api/products',note='Should fail')
	# p.110
	s.send('curl ' + URL + '/api/products -H "Host: apiserver.istioinaction.io"',note='Overriding the host should work')
	# Securing (p.112)
	# Istio's gateway implementation allows us to terminate incoming TLS/SSL traffic
		# pass it through to the backend services,
		# redirect any non-TLS traffic to the proper TLS ports as well as
		# implement mutual TLS.
	s.send('kubectl create -n istio-system secret tls istio-ingressgateway-certs --key chapter-files/chapter4/certs/3_application/private/apiserver.istioinaction.io.key.pem --cert chapter-files/chapter4/certs/3_application/certs/apiserver.istioinaction.io.cert.pem',note='Start by creating the istio-ingressgateway-certs secret')
	s.send('kubectl replace -f chapter-files/chapter4/coolstore-gw-tls.yaml',note='configure the gateway to use these certs/secrets')
	s.send('kubectl replace -f chapter-files/chapter4/coolstore-gw-tls.yaml',note='replace gateway with new gateway resource')
	HTTPS_PORT = s.send_and_get_output("""kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}'""",note='Get https port for ingressgateway service')
	URL = HTTP_HOST + ':' + HTTP_PORT
	s.send('curl -v -H "Host: apiserver.istioinaction.io" https://' + URL + '/api/products',note='Should fail, as no cert')
	s.send('curl -v -H "Host: apiserver.istioinaction.io" https://' + URL + '/api/products --cacert chapter-files/chapter4/certs/2_intermediate/certs/ca-chain.cert.pem',note='Will stil fail because host is wrong')
	s.send('curl -H "Host: apiserver.istioinaction.io" https://apiserver.istioinaction.io:' + HTTPS_PORT + '/api/products --cacert chapter-files/chapter4/certs/2_intermediate/certs/ca-chain.cert.pem --resolve apiserver.istioinaction.io:' + HTTPS_PORT + ':' + HTTPS_HOST,note='Now should see a 200 OK')
	s.send('kubectl replace -f chapter-files/chapter4/coolstore-gw-tls-redirect.yaml',note='Redirect http to https')
	s.send("""curl -v $(minikube ip):$(kubectl -n istio-system get service istio-ingressway -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}')/api/products -H "Host: apiserver.istioinaction.io" """,note='Call ingress gateway on http port, should get a 301 redirect to https.')
	s.send('kubectl create -n istio-system secret generic istio-ingressgateway-ca-certs --from-file=chapter-files/chapter4/certs/2_intermediate/certs/ca-chain.cert.pem',note='Now doing mtls, set up ca certs secrets')
	s.send('kubectl replace -f chapter-files/chapter4/coolstore-gw-mtls.yaml',note='mTLS gateway config')
	s.send('curl -H "Host: apiserver.istioinaction.io" https://apiserver.istioinaction.io:' + HTTPS_PORT + '/api/products --cacert chapter-files/chapter4/certs/2_intermediate/certs/ca-chain.cert.pem --resolve apiserver.istioinaction.io:' + HTTPS_PORT + ':' + HTTPS_HOST,note='Same call as before should be rejected, as we are only passing the CA cert chain to the curl command. Need to pass the client cert and private key with the --cert and --key parameters as per next command')
	# p.122
	s.send('curl -H "Host: apiserver.istioinaction.io" https://apiserver.istioinaction.io:' + HTTPS_PORT + '/api/products --cacert chapter-files/chapter4/certs/2_intermediate/certs/ca-chain.cert.pem --resolve apiserver.istioinaction.io:' + HTTPS_PORT + ':' + HTTPS_HOST + ' --cert chapter-files/chapter4/certs/4_client/certs/apiserver.istioinaction.io.cert.pem --key chapter-files/chapter4/certs/4_client/private/apiserver.istioinaction.io.key.pem',note='should see a 200 and JSON')
	# 4.3.4 Serving multuiple virtual hosts with TLS
	s.send('kubectl create -n istio-system secret tls catalog-ingressgateway-certs --key chapter-files/chapter4/certs2/3_application/private/catalog.istioinaction.io.key.pem --cert chapter-files/chapter4/certs2/3_application/certs/catalog.istioinaction.io.cert.pem',note="Create extra certs and keys for the multiple virtual hosts")
	s.send('kubectl replace -f chapter-files/chapter4/istio-ingressgateway-deployment-catalog-certs.yaml',note='Create gateway for multiple tls certs')
	s.send('kubectl replace -f chapter-files/chapter4/coolstore-gw-multi-tls.yaml',note='Update gateway configuration')
	s.send('kubectl replace -f chapter-files/chapter4/catalog-vs.yaml',note='Add catalog virtual service')
	s.send('curl -H "Host: apiserver.istioinaction.io" https://apiserver.istioinaction.io:' + HTTPS_PORT + '/api/products --cacert chapter-files/chapter4/certs/2_intermediate/certs/ca-chain.cert.pem --resolve apiserver.istioinaction.io:' + HTTPS_PORT + ':' + HTTPS_HOST,note='This call should work as per the simple TLS section')
	s.send('curl -H "Host: catalog.istioinaction.io" https://catalog.istioinaction.io:' + HTTPS_PORT + '/api/catalog --cacert chapter-files/chapter4/certs2/2_intermediate/certs/ca-chain.cert.pem --resolve catalog.istioinaction.io:' + HTTPS_PORT + ':' + HTTPS_HOST,note='Should also work - uses SNI to know which cert to present to which client')
	# p.123 - TCP traffic
	s.send('kubectl create -f <(istioctl kube-inject -f chapter-files/chapter4/echo.yaml)',note='Create simple TCP echo service from https://github.com/cjimti/go-echo/')
	# p.124 -
	s.send('kubectl create -f chapter-files/chapter4/gateway-tcp.yaml',note='Expose port 31400 on default istio-ingressgateway, and expose as NodePort on 31400')
	# p.125 -
	s.send('kubectl create -f chapter-files/chapter4/echo-vs.yaml',note='Now port is exposed on the ingress gateway, route traffic to the echo service')
	TCP_PORT = s.send_and_get_output("kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="tcp")].nodePort}'",note='Get tcp port from gateway spec')
	s.pause_point('telnet $(minikube ip) ' + TCP_PORT,note='connect to tcp service')
	# 4.4.2 - traffic routing with SNI and TLS - TODO
	s.pause_point('done ch4')
