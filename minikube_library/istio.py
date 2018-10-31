# TODO

def do_istio(s, version):
	s.send('rm -rf istiotmp')
	s.send('mkdir -p istiotmp')
	s.send('cd istiotmp')
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
	# Ingress gateway - TODO: should this be in istio-system or istioinaction?
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
	s.send('''GRAFANA=$(kubectl -n istio-system get pod | grep -i running | grep grafana | cut -d ' ' -f 1)''')
	s.send('''kubectl port-forward -n istio-system "${GRAFANA}" 8080:3000 &''')
	s.pause_point('now go to localhost:8080')
	s.send('''TRACING=$(kubectl -n istio-system get pod | grep istio-tracing | cut -d ' ' -f 1)''')
	s.send('''kubectl port-forward -n istio-system "${TRACING}" 8181:16686 &''')
	s.pause_point('now go to localhost:8081')
	# Generate a failure
	s.send('''curl ${URL}/api/products -H "failure-percentage: 100"''')
	# Ingress gateway - TODO: should this be in istio-system or istioinaction?
	s.send('''kubectl create -f chapter-files/chapter2/catalog-virtualservice.yaml''')
	# Generate traffic
	for _ in []*10:
		s.send('''curl $URL/api/products -H "failure-percentage: 50"''')
	s.send('kubectl create -f <(istioctl kube-inject -f ./install/catalog-v2-service/catalog-v2-deployment.yaml)'
	s.send('kubectl create -f chapter-files/chapter2/catalog-destinationrule.yaml')
	s.send('kubectl apply -f chapter-files/chapter2/catalog-virtualservice-all-v1.yaml')
	# v1 responses only now
	for _ in []*5:
		s.send('''curl $URL/api/products''')
	s.pause_point('ch2 done')
	s.send('kill %1')
	s.send('kill %2')
	s.pause_point('p58')
