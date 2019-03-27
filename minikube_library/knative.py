def do_knative(s):
	# https://github.com/knative/docs/blob/master/docs/install/Knative-with-Minikube.md
	s.send('kubectl apply --filename https://github.com/knative/serving/releases/download/v0.4.0/istio-crds.yaml')
	s.send("""curl -L https://github.com/knative/serving/releases/download/v0.4.0/istio.yaml | sed 's/LoadBalancer/NodePort/' | kubectl apply --filename -""")
	# Label the default namespace with istio-injection=enabled.
	s.send('kubectl label --overwrite namespace default istio-injection=enabled')
	s.send_until('kubectl get pod -n istio-system | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0',cadence=20)
	s.send("""curl -L https://github.com/knative/serving/releases/download/v0.4.0/serving.yaml | sed 's/LoadBalancer/NodePort/' | kubectl apply --filename -""")
	s.send_until('kubectl get pod -n knative-serving | grep -v ^NAME | grep -v Running | wc -l','0',cadence=20)
	s.send('INGRESSGATEWAY=knative-ingressgateway')
	# The use of `knative-ingressgateway` is deprecated in Knative v0.3.x.
	# Use `istio-ingressgateway` instead, since `knative-ingressgateway`
	# will be removed in Knative v0.4.
	s.send('''if kubectl get configmap config-istio -n knative-serving &> /dev/null; then INGRESSGATEWAY=istio-ingressgateway; fi''')
	s.send('''echo $(minikube ip):$(kubectl get svc $INGRESSGATEWAY --namespace istio-system --output 'jsonpath={.spec.ports[?(@.port==80)].nodePort}')''')
