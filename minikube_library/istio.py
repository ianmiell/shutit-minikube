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

def do_istioinaction(s):
	# Create istioinaction namespace
	s.send('kubectl create namespace istioinaction')
	s.send('kubectl config set-context $(kubectl config current-context) --namespace=istioinaction')
	s.send('cd ../book-source-code')
	# Deploy catalog app
	s.send('kubectl create -f <(istioctl kube-inject -f install/catalog-service/catalog-all.yaml)')
	s.send_until('kubectl get pod | grep catalog | wc -l','1')
	s.send_until('kubectl get pod | grep catalog | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0', cadence=20)
	s.send('sleep 60')
	s.send("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl --command -- sh -c 'curl -s catalog:8080/api/catalog'")
	# Deploy API gateway service
	s.send('kubectl create -f <(istioctl kube-inject -f install/apigateway-service/apigateway-all.yaml)')
	s.send_until('kubectl get pod | grep apigateway | wc -l','1')
	s.send_until('kubectl get pod | grep apigateway | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0', cadence=20)
	s.send('sleep 60')
	s.send("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl --command -- sh -c 'curl -s apigateway:8080/api/products'")

	# Ingress gateway in istio-system
	s.send('kubectl config set-context $(kubectl config current-context) --namespace=istio-system')
	s.send('kubectl create -f chapter-files/chapter2/ingress-gateway.yaml')
	s.send("""URL=$(minikube ip):$(kubectl get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')""")
	s.send('curl ${URL}/api/products')
	# Debug
	s.send("istioctl proxy-config routes $(kubectl get pod | grep ingress | cut -d ' ' -f 1)")

	# Back to istioinaction
	s.send('kubectl config set-context $(kubectl config current-context) --namespace=istioinaction')
	s.send('kubectl get gateway')
	s.send('kubectl get virtualservice')
	# Generate some traffic
	for _ in []*5:
		s.send('do curl $URL/api/products; sleep .5; done')
	# Grafana
	s.send('sleep 60')
	s.send('''kubectl -n istio-system get pod | grep -i running | grep grafana | cut -d ' ' -f 1''')
	s.send('''GRAFANA=$(kubectl -n istio-system get pod | grep -i running | grep grafana | cut -d ' ' -f 1)''')
	random_port = str(random.randrange(49152,65535))
	s.send('''kubectl port-forward -n istio-system "${GRAFANA}" ''' + random_port + ''':3000 &''')
	s.pause_point('now go to localhost:' + random_port)
	# Jaeger tracing
	s.send('sleep 60')
	s.send('''kubectl -n istio-system get pod | grep istio-tracing | cut -d ' ' -f 1''')
	s.send('''TRACING=$(kubectl -n istio-system get pod | grep istio-tracing | cut -d ' ' -f 1)''')
	random_port = str(random.randrange(49152,65535))
	s.send('''kubectl port-forward -n istio-system "${TRACING}" ''' + random_port + ''':16686 &''')
	s.pause_point('now go to localhost:' + random_port)
	# Generate a failure
	s.send('''curl ${URL}/api/products -H "failure-percentage: 100"''')
	# Ingress gateway
	s.send('''kubectl create -f chapter-files/chapter2/catalog-virtualservice.yaml''')
	# Generate traffic
	for _ in []*10:
		s.send('''curl $URL/api/products -H "failure-percentage: 50"''')
	s.send('kubectl create -f <(istioctl kube-inject -f ./install/catalog-v2-service/catalog-v2-deployment.yaml)')
	s.send('kubectl create -f chapter-files/chapter2/catalog-destinationrule.yaml')
	s.send('kubectl apply -f chapter-files/chapter2/catalog-virtualservice-all-v1.yaml')
	# v1 responses only now
	for _ in []*5:
		s.send('''curl $URL/api/products''')
	# Create version 2 of the service, only available through dark launch.
	s.send('kubectl apply -f chapter-files/chapter2/catalog-virtualservice-dark-v2.yaml')
	for _ in []*5:
		s.send('''curl $URL/api/products''')
	# Call 'dark launch'
	s.send('curl $URL/api/products -H "x-dark-launch: v2"')
	s.send('kill %1')
	s.send('kill %2')
	s.send('''eval $(minikube docker-env)''')
	s.send('docker ps')
	s.send('docker pull istioinaction/envoy:v1.7.0')
	s.send('docker pull tutum/curl')
	s.send('docker pull citizenstig/httpbin')
	s.send('docker run -d --name httpbin citizenstig/httpbin')
	s.send('docker run -it --rm --link httpbin tutum/curl curl -X GET http://httpbin:8000/headers')
	# Show envy help
	s.send('docker run -it --rm istioinaction/envoy:v1.7.0 envoy --help')
	# Run envoy with no config (will fail)
	s.send('docker run -it --rm istioinaction/envoy:v1.7.0 envoy || true')
	s.send('docker run -i --rm --entrypoint "cat" istioinaction/envoy:v1.7.0 /etc/envoy/simple.yaml')
	s.send('docker run -i --rm --link httpbin istioinaction/envoy:v1.7.0 --entrypoint cat envoy /etc/envoy/simple.yaml')
	# Run sith a simple config (cat'd above)
	s.send('docker run -d --name proxy --link httpbin istioinaction/envoy:v1.7.0 envoy -c /etc/envoy/simple.yaml')
	s.send('docker logs proxy')
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15001/headers')
	# Delete proxy
	s.send('docker rm -f proxy')
	# Show diff between last config and new one
	s.send('docker run -i --rm --link httpbin istioinaction/envoy:v1.7.0 --entrypoint diff envoy /etc/envoy/simple.yaml /etc/envoy/simple_change_timeout.yaml')
	# Run again, but change timeout (different config)
	s.send('docker run -d --name proxy --link httpbin istioinaction/envoy:v1.7.0 envoy -c /etc/envoy/simple_change_timeout.yaml')
	# Get headers
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15001/headers')
	# Get stats
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/stats')
	# Too much crap - now grep for retry
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/stats | grep retry')
	# Get list of endpoints - explore!
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/')
	# Delete proxy
	s.send('docker rm -f proxy')
	# Run again, but change retry policy
	s.send('docker run -d --name proxy --link httpbin istioinaction/envoy:v1.7.0 envoy -c /etc/envoy/simple_retry.yaml')
	# create a 500 error by calling /status/500
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15001/status/500')
	# what happened?
	s.send('docker run -it --rm --link proxy tutum/curl curl -X GET http://proxy:15000/stats | grep retry')
	# CHAPTER 4
	s.send('INGRESS_POD=$(kubectl get pod -n istio-system | grep ingressgateway | cut -d ' ' -f 1)')
	s.send('kubectl -n istio-system exec $INGRESS_POD ps aux')
	s.send'kubectl create -f chapter-files/chapter4/coolstore-gw.yaml')
	s.send('istioctl proxy-config listener $INGRESS_POD -n istio-system')
	s.pause_point('doing ch4')
