def do_admission_controller_mutating(s):
	# See: https://github.com/jasonrichardsmith/mwcexample
	# See: https://container-solutions.com/some-admission-webhook-basics/
	s.send('rm -rf ~/minikube_tmp/admission_controller')
	s.send('mkdir -p ~/minikube_tmp/admission_controller')
	s.send('cd ~/minikube_tmp/admission_controller')
	s.send('git clone https://github.com/jasonrichardsmith/mwcexample')
	s.send('cd mwcexample')
	s.send('''sed -i 's/jasonrichardsmith/imiell/' Makefile''')
	s.send('''sed -i 's/jasonrichardsmith/imiell/' manifest.yaml''')
	#s.send('make minikube',note='make the container')
	s.send('eval $(minikube docker-env)')
	s.pause_point('docker login')
	s.send('make && make push',note='load it up(?)')
	s.send('kubectl apply -f ns.yaml',note='Make the namespace')
	s.send('./gen-cert.sh',note=r'''Generate the certs. Aside from the openssl work, the
kubectl commands used are:
# delete any previous certificate signing requests
kubectl delete csr ${csrName} 2>/dev/null || true
# create csr with:
cat <<EOF | kubectl create -f -
apiVersion: certificates.k8s.io/v1beta1
kind: CertificateSigningRequest
metadata:
  name: ${csrName}
spec:
  groups:
  - system:authenticated
  request: $(cat ${tmpdir}/server.csr | base64 | tr -d '\n')
  usages:
  - digital signature
  - key encipherment
  - server auth
EOF
# Check it's been added
kubectl get csr ${csrName}
# Approve the csr
kubectl certificate approve ${csrName}
# Check it's been approved
kubectl get csr ${csrName} -o jsonpath='{.status.certificate}'
# Create the secret with the server key and cert
kubectl create secret generic ${title} --from-file=key.pem=${tmpdir}/server-key.pem --from-file=cert.pem=${tmpdir}/server-cert.pem --dry-run -o yaml | kubectl -n ${title} apply -f
''')
	s.send('./ca-bundle.sh',note="""Creates a ca bundle(?) with:

kubectl get configmap -n kube-system extension-apiserver-authentication -o=jsonpath='{.data.client-ca-file}'

the output of which is placed in an exported variable (CA_BUNDLE) and then sub into the deployment/service setup etc in manifest.yaml, which contains the mutating webhook:

apiVersion: admissionregistration.k8s.io/v1beta1
kind: MutatingWebhookConfiguration
metadata:
  name: mwc-example
webhooks:
  - name: mwc-example.jasonrichardsmith.com
    clientConfig:
      service:
        name: mwc-example
        namespace: mwc-example
        path: "/mutating-pods"
      caBundle: "${CA_BUNDLE}"
    rules:
      - operations: ["CREATE","UPDATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
    failurePolicy: Fail
    namespaceSelector:
      matchLabels:
        mwc-example: enabled""")
	s.send('kubectl apply -f manifest-ca.yaml',note='deploy the created manifest.yaml')
	s.send('kubectl apply -f test.yaml',note='Now deploy the test.yaml - Which if you inspect you will see the namespace has a label - mwc-enable: enabled')
	s.send('kubectl get pods -n mwc-test -o json | jq .items[0].metadata.labels')
	s.pause_point('play')

def do_admission_controller_validating(s):
	# https://banzaicloud.com/blog/k8s-admission-webhooks/
	# https://github.com/banzaicloud/admission-webhook-example/tree/blog
	s.send('rm -rf ~/minikube_tmp/admission_controller')
	s.send('mkdir -p ~/minikube_tmp/admission_controller')
	s.send('cd ~/minikube_tmp/admission_controller')
	s.send('git clone git@github.com:banzaicloud/admission-webhook-example.git')
	s.send('cd admission-webhook-example')
	s.send('git checkout blog')
	s.pause_point('https://banzaicloud.com/blog/k8s-admission-webhooks/')


#https://medium.com/ibm-cloud/diving-into-kubernetes-mutatingadmissionwebhook-6ef3c5695f74
def do_admission_controller_other(s):
	s.send('rm -rf ~/minikube_tmp/admission_controller')
	s.send('mkdir -p ~/minikube_tmp/admission_controller')
	s.send('cd ~/minikube_tmp/admission_controller')
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
