def do_knative(s):
	# https://github.com/knative/docs/blob/master/docs/install/Knative-with-Minikube.md
	s.send('''kubectl apply --filename https://raw.githubusercontent.com/knative/serving/v0.7.0/third_party/istio-1.1.7/istio-crds.yaml''')
	s.send('''sleep 120''')
	s.send('''curl -L https://raw.githubusercontent.com/knative/serving/v0.7.0/third_party/istio-1.1.7/istio.yaml | sed 's/LoadBalancer/NodePort/'   | kubectl apply --filename -''')
	s.send('''sleep 10''')
	# Label the default namespace with istio-injection=enabled.
	s.send('kubectl label --overwrite namespace default istio-injection=enabled')
	s.send_until('kubectl get pod -n istio-system | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0',cadence=20)
	s.send('kubectl delete svc knative-ingressgateway -n istio-system || true')
	s.send('kubectl delete deploy knative-ingressgateway -n istio-system || true')
	s.send('kubectl delete statefulset/controller-manager -n knative-sources || true')
	s.send('''sleep 10''')
	s.send('kubectl apply --selector knative.dev/crd-install=true --filename https://github.com/knative/serving/releases/download/v0.7.0/serving.yaml --filename https://github.com/knative/build/releases/download/v0.7.0/build.yaml --filename https://github.com/knative/eventing/releases/download/v0.7.0/release.yaml --filename https://github.com/knative/serving/releases/download/v0.7.0/monitoring.yaml')
	s.send('''sleep 30''')
	s.send('kubectl apply --filename https://github.com/knative/serving/releases/download/v0.7.0/serving.yaml --selector networking.knative.dev/certificate-provider!=cert-manager --filename https://github.com/knative/build/releases/download/v0.7.0/build.yaml --filename https://github.com/knative/eventing/releases/download/v0.7.0/release.yaml --filename https://github.com/knative/serving/releases/download/v0.7.0/monitoring.yaml')
	s.send_until('kubectl get pods --namespace knative-serving | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)
	s.send_until('kubectl get pods --namespace knative-build | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)
	s.send_until('kubectl get pods --namespace knative-eventing | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)
	s.send_until('kubectl get pods --namespace knative-monitoring | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)

