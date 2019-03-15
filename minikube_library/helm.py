def do_helm(s):
	# Get helm
	if not s.command_available('helm'):
		# https://docs.helm.sh/using_helm/#installing-the-helm-client
		s.send('curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash')


	# From: https://helm.sh/docs/using_helm/#example-service-account-with-cluster-admin-role
	# NAMESPACE LEVEL HELM
	s.send('kubectl create namespace tiller-confined')
	s.send_file('ns-role-tiller.yaml','''kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tiller-nsmanager
  namespace: tiller-confined
rules:
- apiGroups: ["", "batch", "extensions", "apps"]
  resources: ["*"]
  verbs: ["*"]''')
	s.send('kubectl create -f ns-role-tiller.yaml')
	s.send_file('ns-role-binding.yaml','''apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller-confined-sa
  namespace: tiller-confined
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tiller-binding
  namespace: tiller-confined
subjects:
- kind: ServiceAccount
  name: tiller-confined-sa
  namespace: tiller-confined
roleRef:
  kind: Role
  name: tiller-nsmanager
  apiGroup: rbac.authorization.k8s.io''')
	s.send('kubectl create -f ns-role-binding.yaml')
	s.send('helm init --service-account tiller-confined-sa --tiller-namespace tiller-confined')

	s.send('kubectl create namespace tiller-confined2')
	s.send_file('ns-role-tiller2.yaml','''apiVersion: v1
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tiller-nsmanager2
  namespace: tiller-confined2
rules:
- apiGroups: ["", "batch", "extensions", "apps"]
  resources: ["*"]
  verbs: ["*"]''')
	s.send_file('ns-role-binding2.yaml','''apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller-confined-sa2
  namespace: tiller-confined2
---
apiVersion: v1
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tiller-binding2
  namespace: tiller-confined2
subjects:
- kind: ServiceAccount
  name: tiller-confined-sa2
  namespace: tiller-confined2
roleRef:
  kind: Role
  name: tiller-nsmanager2
  apiGroup: rbac.authorization.k8s.io''')
	s.send('kubectl create -f ns-role-binding2.yaml')
	# Get the yaml only
	#s.send('helm init --service-account tiller-confined-sa2 --tiller-namespace tiller-confined2 -o yaml')
	s.send('helm init --service-account tiller-confined-sa2 --tiller-namespace tiller-confined2')
	s.pause_point('')

	# CLUSTER LEVEL HELM
	# Create cluster admin role
	s.send_file('rbac-config.yaml','''apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: tiller
    namespace: kube-system''')

	s.send('kubectl create -f rbac-config.yaml')
	s.send('kubectl get pods --all-namespaces')
	s.send('helm init --service-account tiller --tiller-namespace kube-system')
	s.send('kubectl get pods --all-namespaces')
	s.pause_point('')
