def do_knative(s):
	# https://github.com/knative/docs/blob/master/docs/install/Knative-with-Minikube.md
	s.send('''kubectl apply --filename https://raw.githubusercontent.com/knative/serving/v0.7.0/third_party/istio-1.1.7/istio-crds.yaml''')
	s.send('''sleep 30''')
	s.send('''curl -L https://raw.githubusercontent.com/knative/serving/v0.7.0/third_party/istio-1.1.7/istio.yaml | sed 's/LoadBalancer/NodePort/'   | kubectl apply --filename -''')
	s.send('''sleep 10''')
	# Label the default namespace with istio-injection=enabled.
	s.send('kubectl label --overwrite namespace default istio-injection=enabled')
	s.send_until('kubectl get pod -n istio-system | grep -v ^NAME | grep -v Running | grep -v Completed | wc -l','0',cadence=20)
	s.send('''sleep 10''')
	s.send('kubectl apply --selector knative.dev/crd-install=true --filename https://github.com/knative/serving/releases/download/v0.7.0/serving.yaml --filename https://github.com/knative/build/releases/download/v0.7.0/build.yaml --filename https://github.com/knative/eventing/releases/download/v0.7.0/release.yaml --filename https://github.com/knative/serving/releases/download/v0.7.0/monitoring.yaml')
	s.send('''sleep 10''')
	# Run twice so that error is not seen again.
	s.send('kubectl apply --selector knative.dev/crd-install=true --filename https://github.com/knative/serving/releases/download/v0.7.0/serving.yaml --filename https://github.com/knative/build/releases/download/v0.7.0/build.yaml --filename https://github.com/knative/eventing/releases/download/v0.7.0/release.yaml --filename https://github.com/knative/serving/releases/download/v0.7.0/monitoring.yaml')
	s.send('''sleep 30''')
	# Then run again.
	s.send('kubectl apply --filename https://github.com/knative/serving/releases/download/v0.7.0/serving.yaml --selector networking.knative.dev/certificate-provider!=cert-manager --filename https://github.com/knative/build/releases/download/v0.7.0/build.yaml --filename https://github.com/knative/eventing/releases/download/v0.7.0/release.yaml --filename https://github.com/knative/serving/releases/download/v0.7.0/monitoring.yaml')
	s.send_until('kubectl get pods --namespace knative-serving | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)
	s.send_until('kubectl get pods --namespace knative-build | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)
	s.send_until('kubectl get pods --namespace knative-eventing | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)
	s.send_until('kubectl get pods --namespace knative-monitoring | grep -v ^NAME | grep -v Running | wc -l','0', cadence=20)


def do_kubernetes_eventing(s):
	# https://knative.dev/docs/eventing/samples/kubernetes-event-source/
	#s.send('kubectl create namespace default')
	s.send('kubectl config set-context --current --namespace=default')
	s.send('kubectl label namespace default knative-eventing-injection=enabled')
	# Create a Service Account that the ApiServerSource runs as.
	# The ApiServerSource watches for Kubernetes events and forwards them to the Knative Eventing Broker.
	# Create a file named serviceaccount.yaml and copy the code block below into it.
	s.send_file('serviceaccount.yaml', '''apiVersion: serving.knative.dev/v1alpha1
apiVersion: v1
kind: ServiceAccount
metadata:
  name: events-sa
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: event-watcher
rules:
  - apiGroups:
      - ""
    resources:
      - events
    verbs:
      - get
      - list
      - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: k8s-ra-event-watcher
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: event-watcher
subjects:
  - kind: ServiceAccount
    name: events-sa
    namespace: default''')
	s.send('kubectl create -f serviceaccount.yaml')
	# In order to receive events, you have to create a concrete Event Source for a specific namespace.
	# Create a file named k8s-events.yaml and copy the code block below into it
	s.send_file('k8s-events.yaml','''apiVersion: sources.eventing.knative.dev/v1alpha1
kind: ApiServerSource
metadata:
  name: testevents
  namespace: default
spec:
  serviceAccountName: events-sa
  mode: Resource
  resources:
    - apiVersion: v1
      kind: Event
  sink:
    apiVersion: eventing.knative.dev/v1alpha1
    kind: Broker
    name: default''')
	s.send('kubectl create -f k8s-events.yaml')
	# In order to check the ApiServerSource is fully working, we will create a simple
	# Knative Service that dumps incoming messages to its log and creates a
	# Trigger from the Broker to that Knative Service.
	# Create a file named trigger.yaml and copy the code block below into it.
	# If the deployed ApiServerSource is pointing at a Broker other than default, modify trigger.yaml by adding spec.broker with the Broker’s name.
	s.send_file('trigger.yaml','''apiVersion: eventing.knative.dev/v1alpha1
kind: Trigger
metadata:
  name: testevents-trigger
  namespace: default
spec:
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1alpha1
      kind: Service
      name: event-display
---
# This is a very simple Knative Service that writes the input request to its log.
apiVersion: serving.knative.dev/v1alpha1
kind: Service
metadata:
  name: event-display
  namespace: default
spec:
  template:
    spec:
      containers:
        - # This corresponds to
          # https://github.com/knative/eventing-contrib/blob/release-0.5/cmd/event_display/main.go
          image: gcr.io/knative-releases/github.com/knative/eventing-sources/cmd/event_display@sha256:bf45b3eb1e7fc4cb63d6a5a6416cf696295484a7662e0cf9ccdf5c080542c21d''')
	s.send('kubectl create -f trigger.yaml')
	s.send('sleep 30')
	# Create events by launching a pod in the default namespace. Create a busybox container and immediately delete it.
	s.send('kubectl run busybox --image=busybox --restart=Never -- ls')
	s.send('kubectl delete pod busybox')
	s.send('kubectl get pods')
	s.send('kubectl logs -l serving.knative.dev/service=event-display -c user-container')
	s.pause_point('''

''')
	s.send('kubectl --namespace default delete --filename serviceaccount.yaml')
	s.send('kubectl --namespace default delete --filename k8s-events.yaml')
	s.send('kubectl --namespace default delete --filename trigger.yaml')


def do_cron_eventing(s):
	# https://knative.dev/docs/eventing/samples/cronjob-source/
	s.send('service.yaml', '''apiVersion: serving.knative.dev/v1alpha1
kind: Service
metadata:
  name: event-display
spec:
  template:
    spec:
      containers:
        - image: gcr.io/knative-releases/github.com/knative/eventing-sources/cmd/event_display''')
	s.send('kubectl apply -f service.yaml')
	s.send_file('cronjob-source.yaml', '''apiVersion: sources.eventing.knative.dev/v1alpha1
kind: CronJobSource
metadata:
  name: test-cronjob-source
spec:
  schedule: "*/2 * * * *"
  data: '{"message": "Hello world!"}'
  sink:
    apiVersion: serving.knative.dev/v1alpha1
    kind: Service
    name: event-display''')
	s.send('kubectl apply -f cronjob-source.yaml')
	s.pause_point('''Every two minutes a message should be sent to the event-display service:

kubectl logs -l serving.knative.dev/service=event-display -c user-container --since=10m

''')
	s.send('kubectl delete --filename cronjob-source.yaml')
	s.send('kubectl delete --filename service.yaml')
