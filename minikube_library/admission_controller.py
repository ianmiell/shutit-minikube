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
	s.send('kubectl create namespace opa',note='Create opa namespace')
	s.send('kubectl config set-context opa-tutorial --user minikube --cluster minikube --namespace opa',note='create context')
	s.send('kubectl config use-context opa-tutorial',note='set context')
	s.send('openssl genrsa -out ca.key 2048',note='create a ca key')
	s.send('openssl req -x509 -new -nodes -key ca.key -days 100000 -out ca.crt -subj "/CN=admission_ca"',note='Create X509 CA cert from the key')
	s.send('''cat >server.conf <<EOF
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth, serverAuth
EOF''',note='Create a server.conf file for server csr generation')
	s.send('openssl genrsa -out server.key 2048',note='create a server key')
	s.send('openssl req -new -key server.key -out server.csr -subj "/CN=opa.opa.svc" -config server.conf',note='create server csr opa.opa.svc must match opa service created below')
	s.send('openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 100000 -extensions v3_req -extfile server.conf',note='creaste cert against previously-created CA')
	s.send('kubectl create secret tls opa-server --cert=server.crt --key=server.key',note='create secret to store server cert and key for OPA')
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
EOF''',note='Create admission controller file ClusterRole')
	s.send('''cat >>admission-controller.yaml << 'EOF'
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
EOF''',note='Create admission controller file Role')
	s.send('''cat >>admission-controller.yaml << 'EOF'
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
EOF''',note='Create admission controller file RoleBinding')
	s.send('''cat >>admission-controller.yaml << 'EOF'
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
EOF''',note='Create admission controller file Service')
	s.send('''cat >>admission-controller.yaml << 'EOF'
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
EOF''',note='''Create admission controller file Deployment
The deployment uses the openpolicyagent/opa:0.10.1 image for container 1
and openpolicyagent/kube-mgmt:0.6 for container 2.
volumeMounts loads the certs from the tls secret created earlier.
The 443 port is mapped to the container's 8181 port.''')

	s.send('''cat >>admission-controller.yaml << 'EOF'
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
EOF''',note='''Create admission controller file AdmissionReview
This creates the opa-default-system-main, which presumably the opa image expects.
Try changing it to see what happens. TODO
So main evaluates to the Admission Review response, which leads onto the response.
The response defaults to allowed if the 'response = {' doesn't evaluate all to true
Note that the last item is a !=
so if the reason is empty it evalates to false and returns allowed: true back
to the doc.
''')
	s.send('kubectl apply -f admission-controller.yaml',note='Apply the settings')
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
EOF''',note='Create the webhook configuration yaml, passing in the b64-encoded ca
Applies to all resources, apigroups and apiversions for CREATE and UPDATE operations and the service in opa running in opa')
	s.send('kubectl apply -f webhook-configuration.yaml',note='Apply the webhook configuration yaml')
	# package - kubernetes.admission
	#   referred to in the ConfigMap opa-default-system-main
	# import - data.kubernetes.namespaces - gives access to the namespaces.
	# 
	# The whitelist is grabbed from ingress.
	s.send('''cat >ingress-whitelist.rego << EOF
package kubernetes.admission

import data.kubernetes.namespaces

deny[msg] {
    input.request.kind.kind = "Ingress"
    input.request.operation = "CREATE"
    host = input.request.object.spec.rules[_].host
    not fqdn_matches_any(host, valid_ingress_hosts)
    msg = sprintf("invalid ingress host %q", [host])
}

valid_ingress_hosts = {host |
    whitelist = namespaces[input.request.namespace].metadata.annotations["ingress-whitelist"]
    hosts = split(whitelist, ",")
    host = hosts[_]
}

fqdn_matches_any(str, patterns) {
    fqdn_matches(str, patterns[_])
}

fqdn_matches(str, pattern) {
    pattern_parts = split(pattern, ".")
    pattern_parts[0] = "*"
    str_parts = split(str, ".")
    n_pattern_parts = count(pattern_parts)
    n_str_parts = count(str_parts)
    suffix = trim(pattern, "*.")
    endswith(str, suffix)
}

fqdn_matches(str, pattern) {
    not contains(pattern, "*")
    str = pattern
}
EOF''',note='''Set up an ingress whitelist rego file (TODO: what does it do?)

deny will deny Ingress CREATE actions. How do we add another type?
''')
	s.send('kubectl create configmap ingress-whitelist --from-file=ingress-whitelist.rego',note='Create configmap from rego file called ingress-whitelist')
	s.send('''cat >qa-namespace.yaml << EOF
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    ingress-whitelist: "*.qa.acmecorp.com,*.internal.acmecorp.com"
  name: qa
EOF''',note='Create a qa namespace with a longer ingress whitelist with internal urls')
	s.send('''cat >production-namespace.yaml << EOF
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    ingress-whitelist: "*.acmecorp.com"
  name: production
EOF''',note='Create a prod namespace with a shorter ingress whitelist')
	s.send('kubectl create -f qa-namespace.yaml',note='create qa namespace')
	s.send('kubectl create -f production-namespace.yaml',note='create prod namespace')
	s.send('''cat >ingress-ok.yaml << EOF
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-ok
spec:
  rules:
  - host: signin.acmecorp.com
    http:
      paths:
      - backend:
          serviceName: nginx
          servicePort: 80
EOF''',note='Create an acceptable ingress object.')
	s.send('''cat >ingress-bad.yaml << EOF
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-bad
spec:
  rules:
  - host: acmecorp.com
    http:
      paths:
      - backend:
          serviceName: nginx
          servicePort: 80
EOF''',note='Create a BAD ingress object')
	s.send('kubectl create -f ingress-ok.yaml -n production',note='ok object is fine for prod')
	s.send('kubectl create -f ingress-bad.yaml -n qa',note='bad object is not acceptable for qa')
	s.send('''cat >ingress-conflicts.rego << EOF
package kubernetes.admission

import data.kubernetes.ingresses

deny[msg] {
    input.request.kind.kind = "Ingress"
    input.request.operation = "CREATE"
    host = input.request.object.spec.rules[_].host
    ingress = ingresses[other_ns][other_ingress]
    other_ns != input.request.namespace
    ingress.spec.rules[_].host = host
    msg = sprintf("invalid ingress host %q (conflicts with %v/%v)", [host, other_ns, other_ingress])
}
EOF''',note='Now create a policy that rejects ingress objects in different namesapces that share the same hostname')
	s.send('kubectl create configmap ingress-conflicts --from-file=ingress-conflicts.rego',note='create the configmap that stores the rules')
	s.send('kubectl get configmap ingress-conflicts -o yaml',note='check it was installed correctly')
	s.send('''cat >staging-namespace.yaml << EOF
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    ingress-whitelist: "*.acmecorp.com"
  name: staging
EOF''',note='Try and create a namespace with a whitelist used before')
	s.send('kubectl create -f staging-namespace.yaml',note='Create the namespace')
	s.send('kubectl create -f ingress-ok.yaml -n staging',note='Fails, as namespace used before')
	s.pause_point('OK?')





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
