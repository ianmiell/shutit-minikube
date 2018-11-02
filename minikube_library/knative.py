def do_knative(s):
	# From: https://github.com/knative/docs/blob/master/install/Knative-with-Minikube.md
	s.send("curl -L https://raw.githubusercontent.com/knative/serving/v0.1.1/third_party/istio-0.8.0/istio.yaml | sed 's/LoadBalancer/NodePort/' | kubectl apply --filename -")
	s.send('kubectl label namespace default istio-injection=enabled')
	# statsd fails for some reason?
	s.send_until('kubectl get pod -n istio-system | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0',cadence=20)
	s.send('''curl -L https://github.com/knative/serving/releases/download/v0.1.1/release-lite.yaml | sed 's/LoadBalancer/NodePort/' | kubectl apply --filename -''')
	s.send_until('kubectl get pod -n knative-serving | grep -v ^NAME | grep -v Running | wc -l','0',cadence=20)
	s.send('sleep 60')
	s.send('''echo $(minikube ip):$(kubectl get svc knative-ingressgateway --namespace istio-system --output 'jsonpath={.spec.ports[?(@.port==80)].nodePort}')''')
	# https://github.com/knative/docs/blob/master/install/getting-started-knative-app.md
	s.run_script('''cat > service.yaml << END
apiVersion: serving.knative.dev/v1alpha1 # Current version of Knative
kind: Service
metadata:
  name: helloworld-go # The name of the app
  namespace: default # The namespace the app will use
spec:
  runLatest:
    configuration:
      revisionTemplate:
        spec:
          container:
            image: gcr.io/knative-samples/helloworld-go # The URL to the image of the app
            env:
            - name: TARGET # The environment variable printed out by the sample app
              value: "Go Sample v1"
END
kubectl apply --filename service.yaml''')
	s.pause_point('continue in getting-started-knative-app.md')
