def do_admission_controller(s):
	# See: https://github.com/jasonrichardsmith/mwcexample
	# See: https://container-solutions.com/some-admission-webhook-basics/
	s.send('rm -rf ~/minikube_tmp/admission_controlller')
	s.send('mkdir -p ~/minikube_tmp/admission_controlller')
	s.send('cd ~/minikube_tmp/admission_controlller')
	s.send('git clone https://github.com/jasonrichardsmith/mwcexample')
	s.send('cd mwcexample')
	s.send('make minikube')
	s.send('make')
	# No need to push as it's to another user's docker repo
	#s.send('make push')
	# TODO: annotate based on webhook basics above
	s.send('kubectl apply -f ns.yaml')
	s.send('./gen-cert.sh')
	s.send('./ca-bundle.sh')
	s.send('kubectl apply -f manifest-ca.yaml')
	s.send('kubectl apply -f test.yaml')
	s.send('kubectl get pods -n mwc-test -o json | jq .items[0].metadata.labels')
	s.pause_point()


#https://medium.com/ibm-cloud/diving-into-kubernetes-mutatingadmissionwebhook-6ef3c5695f74
def do_admission_controller_other(s):
	s.send('rm -rf ~/minikube_tmp/admission_controlller')
	s.send('mkdir -p ~/minikube_tmp/admission_controlller')
	s.send('cd ~/minikube_tmp/admission_controlller')
	s.send('git clone https://github.com/morvencao/kube-mutating-webhook-tutorial')
	s.send('cd kube-mutating-webhook-tutorial')
	s.send('dep ensure')
	s.send('CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o kube-mutating-webhook-tutorial .')
	s.send('docker build --no-cache -t docker.io/imiell/sidecar-injector:v1 .')
	s.send('rm -rf kube-mutating-webhook-tutorial')
	s.send('docker push docker.io/imiell/sidecar-injector:v1')
	s.send('kubectl create -f ./deployment/nginxconfigmap.yaml')
	s.send('kubectl create -f ./deployment/configmap.yaml')
	s.send('./deployment/webhook-create-signed-cert.sh')
	s.send('kubectl create -f ./deployment/deployment.yaml')
	s.send('kubectl create -f ./deployment/service.yaml')
	s.send_until('kubectl get pod','webhook.*Running')
	s.send('cat ./deployment/mutatingwebhook.yaml | ./deployment/webhook-patch-ca-bundle.sh > ./deployment/mutatingwebhook-ca-bundle.yaml')
	s.send('kubectl create -f ./deployment/mutatingwebhook-ca-bundle.yaml')
	s.send('''cat <<EOF | kubectl create -f -
> apiVersion: extensions/v1beta1
> kind: Deployment
> metadata:
>   name: sleep
> spec:
>   replicas: 1
>   template:
>     metadata:
>       annotations:
>         sidecar-injector-webhook.morven.me/inject: "true"
>       labels:
>         app: sleep
>     spec:
>       containers:
>       - name: sleep
>         image: tutum/curl
>         command: ["/bin/sleep","infinity"]
>         imagePullPolicy: IfNotPresent
> EOF''')
	s.send('kubectl get deployment')
	s.send('kubectl get pods')
	s.pause_point('up to kubectl label namespace default sidecar-injector=enabled TODO: annotate')
