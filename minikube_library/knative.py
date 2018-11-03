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
	# DOESN'T WORK?
#	s.run_script('''cat > service.yaml << END
#apiVersion: serving.knative.dev/v1alpha1 # Current version of Knative
#kind: Service
#metadata:
#  name: helloworld-go # The name of the app
#  namespace: default # The namespace the app will use
#spec:
#  runLatest:
#    configuration:
#      revisionTemplate:
#        spec:
#          container:
#            image: gcr.io/knative-samples/helloworld-go # The URL to the image of the app
#            env:
#            - name: TARGET # The environment variable printed out by the sample app
#              value: "Go Sample v1"
#END
#kubectl apply --filename service.yaml''')
	# https://medium.com/@pczarkowski/introduction-to-knative-b93a0b9aeeef
	# See video: https://www.youtube.com/watch?time_continue=179&v=1iSiWOyD7G8
	s.run_script('''cat > build.yaml << END
apiVersion: build.knative.dev/v1alpha1
kind: Build
metadata:
  name: kaniko-build
spec:
  serviceAccountName: build-bot
  source:
    git:
      url: https://github.com/my-user/my-repo
      revision: master
  template:
    name: kaniko
    arguments:
    - name: IMAGE
      value: us.gcr.io/my-project/my-app
END
kubectl apply -f build.yaml
cat > serving.yaml << END
apiVersion: serving.knative.dev/v1alpha1
kind: Service
metadata:
  name: autoscale-go
  namespace: default
spec:
  runLatest:
    configuration:
      revisionTemplate:
        spec:
          container:
            image: samples/autoscale-go
END
cat > eventing.yaml << END
apiVersion: flows.knative.dev/v1alpha1
kind: Flow
metadata:
  name: k8s-event-flow
  namespace: default
spec:
  serviceAccountName: feed-sa
  trigger:
    eventType: dev.knative.k8s.event
    resource: k8sevents/dev.knative.k8s.event
    service: k8sevents
    parameters:
      namespace: default
  action:
    target:
      kind: Route
      apiVersion: serving.knative.dev/v1alpha1
      name: read-k8s-events
END
kubectl apply -f eventing.yaml
''')
	s.pause_point('continue in getting-started-knative-app.md')
