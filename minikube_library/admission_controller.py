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
	## https://banzaicloud.com/blog/k8s-admission-webhooks/
	## https://github.com/banzaicloud/admission-webhook-example/tree/blog
	s.send('rm -rf ~/minikube_tmp/admission_controller')
	s.send('mkdir -p ~/minikube_tmp/admission_controller')
	s.send('cd ~/minikube_tmp/admission_controller')
	s.send('kubectl api-versions')
	s.send('git clone git@github.com:banzaicloud/admission-webhook-example.git')
	s.send('cd admission-webhook-example')
	s.send('git checkout blog')
	s.send('export DOCKER_USER=imiell')
	s.send('./build.sh')
	s.send('./deployment/webhook-create-signed-cert.sh')
	s.send('kubectl get secret admission-webhook-example-certs')
	s.send('kubectl create -f deployment/deployment.yaml')
	s.send('kubectl create -f deployment/service.yaml')
	s.send('cat ./deployment/validatingwebhook.yaml | envsubst > ./deployment/validatingwebhook-ca-bundle.yaml')
	s.send('kubectl label namespace default admission-webhook-example=enabled')
	s.send('kubectl create -f deployment/validatingwebhook-ca-bundle.yaml')
	s.pause_point('''cat ./deployment/validatingwebhook.yaml | ./deployment/webhook-patch-ca-bundle.sh > ./deployment/validatingwebhook-ca-bundle.yaml but with our ca bundle $(kubectl get configmap -n kube-system extension-apiserver-authentication -o=jsonpath='{.data.client-ca-file}' | base64 | tr -d '\n')''')
	s.pause_point('''https://banzaicloud.com/blog/k8s-admission-webhooks/ $(kubectl get configmap -n kube-system extension-apiserver-authentication -o=jsonpath='{.data.client-ca-file}' | base64 | tr -d '\n') from mwcexample''')
	# Above does not work

	# https://github.com/dkoshkin/admission-webhook
	#s.send('git clone https://github.com/dkoshkin/admission-webhook')
	#s.send('cd admission-webhook')
	#s.send('./scripts/pki.sh')
	#s.send('export CA=`cat pki/example/ca.pem | base64`')
	#s.send('export TLS_CERT=`cat pki/example/admission-webhook.pem | base64`')
	#s.send('export TLS_KEY=`cat pki/example/admission-webhook-key.pem | base64`')
	#s.send('./scripts/deploy.sh')
	#s.send('kubectl apply -f examples/')
	#s.pause_point('kubectl get deploy')
	# Above did not work:

	#s.send('git clone https://github.com/ContainerSolutions/go-validation-admission-controller')
	#s.send('cd go-validation-admission-controller')
	#s.send('eval $(minikube docker-env)')
	#s.send('docker build -t namespace-admission .')
	#s.pause_point('https://github.com/ContainerSolutions/go-validation-admission-controller')

def do_admission_controller_opa(s):
	# https://www.openpolicyagent.org/docs/kubernetes-admission-control.html
	s.send('minikube addons enable ingress')
	s.send('kubectl create namespace opa')
	s.send('kubectl config set-context opa-tutorial --user minikube --cluster minikube --namespace opa')
	s.send('kubectl config use-context opa-tutorial')
	s.send('openssl genrsa -out ca.key 2048')
	s.send('openssl req -x509 -new -nodes -key ca.key -days 100000 -out ca.crt -subj "/CN=admission_ca"')
	s.send('''cat >server.conf <<EOF
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth, serverAuth
EOF''')
	s.send('openssl genrsa -out server.key 2048')
	s.send('openssl req -new -key server.key -out server.csr -subj "/CN=opa.opa.svc" -config server.conf',note='opa.opa.svc must match opa service created below')
	s.send('openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 100000 -extensions v3_req -extfile server.conf')
	s.send('kubectl create secret tls opa-server --cert=server.crt --key=server.key',note='create secret to store creds for OPA')
	s.send('''cat >admission-controller.yaml << 'EOF'
# Grant OPA/kube-mgmt read-only access to resources. This let's kube-mgmt
# replicate resources into OPA so they can be used in policies.
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: opa-viewer
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  name: system:serviceaccounts:opa
  apiGroup: rbac.authorization.k8s.io
---
# Define role for OPA/kube-mgmt to update configmaps with policy status.
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: opa
  name: configmap-modifier
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["update", "patch"]
---
# Grant OPA/kube-mgmt role defined above.
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: opa
  name: opa-configmap-modifier
roleRef:
  kind: Role
  name: configmap-modifier
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  name: system:serviceaccounts:opa
  apiGroup: rbac.authorization.k8s.io
---
kind: Service
apiVersion: v1
metadata:
  name: opa
  namespace: opa
spec:
  selector:
    app: opa
  ports:
  - name: https
    protocol: TCP
    port: 443
    targetPort: 443
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  labels:
    app: opa
  namespace: opa
  name: opa
spec:
  replicas: 1
  selector:
    matchLabels:
      app: opa
  template:
    metadata:
      labels:
        app: opa
      name: opa
    spec:
      containers:
        # WARNING: OPA is NOT running with an authorization policy configured. This
        # means that clients can read and write policies in OPA. If you are
        # deploying OPA in an insecure environment, be sure to configure
        # authentication and authorization on the daemon. See the Security page for
        # details: https://www.openpolicyagent.org/docs/security.html.
        - name: opa
          image: openpolicyagent/opa:0.10.1
          args:
            - "run"
            - "--server"
            - "--tls-cert-file=/certs/tls.crt"
            - "--tls-private-key-file=/certs/tls.key"
            - "--addr=0.0.0.0:443"
            - "--addr=http://127.0.0.1:8181"
          volumeMounts:
            - readOnly: true
              mountPath: /certs
              name: opa-server
        - name: kube-mgmt
          image: openpolicyagent/kube-mgmt:0.6
          args:
            - "--replicate-cluster=v1/namespaces"
            - "--replicate=extensions/v1beta1/ingresses"
      volumes:
        - name: opa-server
          secret:
            secretName: opa-server
---
kind: ConfigMap
apiVersion: v1
metadata:
  name: opa-default-system-main
  namespace: opa
data:
  main: |
    package system

    import data.kubernetes.admission

    main = {
      "apiVersion": "admission.k8s.io/v1beta1",
      "kind": "AdmissionReview",
      "response": response,
    }

    default response = {"allowed": true}

    response = {
        "allowed": false,
        "status": {
            "reason": reason,
        },
    } {
        reason = concat(", ", admission.deny)
        reason != ""
    }
EOF''')
	s.send('kubectl apply -f admission-controller.yaml')
	s.send('''cat > webhook-configuration.yaml <<EOF
kind: ValidatingWebhookConfiguration
apiVersion: admissionregistration.k8s.io/v1beta1
metadata:
  name: opa-validating-webhook
webhooks:
  - name: validating-webhook.openpolicyagent.org
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: ["*"]
        apiVersions: ["*"]
        resources: ["*"]
    clientConfig:
      caBundle: $(cat ca.crt | base64 | tr -d '\n')
      service:
        namespace: opa
        name: opa
EOF''')
	s.send('kubectl apply -f webhook-configuration.yaml')
	s.send('''cat >ingress-whitelist.rego << EOF
TODO
EOF''')
	s.send('kubectl create configmap ingress-whitelist --from-file=ingress-whitelist.rego')
	s.send('''cat >qa-namespace.yaml << EOF
TODO
EOF''')
	s.send('''cat >production-namespace.yaml << EOF
TODO
EOF''')
	s.send('kubectl create -f qa-namespace.yaml')
	s.send('kubectl create -f production-namespace.yaml')
	s.send('''cat >ingress-ok.yaml << EOF
TODO
EOF''')
	s.send('''cat >ingress-bad.yaml << EOF
TODO
EOF''')
	s.send('kubectl create -f ingress-ok.yaml -n production')
	s.send('kubectl create -f ingress-bad.yaml -n qa')

	s.pause_point('last one should have failed - TODO 6. and then notes')





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
