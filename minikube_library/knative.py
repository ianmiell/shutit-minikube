def do_knative(s):
	# From: https://github.com/knative/docs/blob/master/install/Knative-with-Minikube.md
	s.send("curl -L https://raw.githubusercontent.com/knative/serving/v0.1.1/third_party/istio-0.8.0/istio.yaml | sed 's/LoadBalancer/NodePort/' | kubectl apply --filename -")
	s.send('kubectl label namespace default istio-injection=enabled')
	s.send_until('kubectl get pod -n istio-system | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0',cadence=20)
	s.send('''curl -L https://github.com/knative/serving/releases/download/v0.1.1/release-lite.yaml | sed 's/LoadBalancer/NodePort/' | kubectl apply --filename -''')
	s.send_until('kubectl get pod -n knative-serving | grep -v ^NAME | grep -v Running | wc -l','0',cadence=20)
	s.send('sleep 60')
	s.send('''echo $(minikube ip):$(kubectl get svc knative-ingressgateway --namespace istio-system --output 'jsonpath={.spec.ports[?(@.port==80)].nodePort}')''')
