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
	s.send_until('kubectl get pod -n istio-system | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0')
	s.send("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl -n istio-system --command -- curl -v 'http://istio-pilot.istio-system:8080/v1/registration'")
	s.send('kubectl create namespace istioinaction')
	s.send('kubectl config set-context $(kubectl config current-context) --namespace=istioinaction')
	s.send('cd ../book-source-code')
	# Deploy catalog app
	s.send('kubectl create -f <(istioctl kube-inject -f install/catalog-service/catalog-all.yaml)')
	s.send_until('kubectl get pod -n istio-system | grep catalog | wc -l','1')
	s.send('sleep 120')
	s.send_until('kubectl get pod -n istio-system | grep catalog | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0')
	s.multisend("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl --command -- sh -c 'curl -s catalog:8080/api/catalog'",{"If you don't see a command prompt, try pressing enter.":''})
	# Deploy API gateway service
	s.send('kubectl create -f <(istioctl kube-inject -f install/apigateway-service/apigateway-all.yaml)')
	s.send_until('kubectl get pod -n istio-system | grep apigateway | wc -l','1')
	s.send_until('kubectl get pod -n istio-system | grep apigateway | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0')
	s.send('sleep 120')
	s.multisend("kubectl run -i --rm --restart=Never dummy --image=byrnedo/alpine-curl --command -- sh -c 'curl -s apigateway:8080/api/products'",{"If you don't see a command prompt, try pressing enter.":''})
	# Ingress gateway
	s.send('kubectl create -f chapter-files/chapter2/ingress-gateway.yaml')
	s.send("URL=$(minikube ip):$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')")
	s.send('curl $URL/api/products')
	# Debug
	s.send("istioctl -n istio-system proxy-config routes $(kubectl get pod -n istio-system | grep ingress | cut -d ' ' -f 1)")
	s.send("kubectl get gateway")
	s.send("kubectl get virtualservice")
	s.pause_point('p57?')
