# Installs helm and flux for global powers.
# Then uses a helm chart to install helm and flux to a specific namespace.

from github import Github
import os
import time

def do_helm_flux(s):

	# Parameterise the tenant namespace
	tenant_ns = 'tenant'

	# GitHub setup
	__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	f = open(os.path.join(__location__, 'github.key'))
	key = f.read().strip()
	g = Github(key)

	# Get helm
	if not s.command_available('helm'):
		# https://docs.helm.sh/using_helm/#installing-the-helm-client
		s.send('curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash')
	# INSTALL HELM GLOBAL
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
	s.send('kubectl get namespaces')

	# FLUX TENANT RBAC
	# Now we have helm global, we now need to create a flux local in the tenant namespace
	# Set up rbac appropriately in prep for flux global to be created, bound to the namespace where appropriate.
	s.send_file('rbac-config-' + tenant_ns + '.yaml','''---
apiVersion: v1
kind: Namespace
metadata:
  labels:
    name: tenant
  name: tenant
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: flux-''' + tenant_ns + '''-role
  namespace: ''' + tenant_ns + '''
rules:
- apiGroups: ["", "*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: flux-''' + tenant_ns + '''-sa
  namespace: ''' + tenant_ns + '''
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: flux-''' + tenant_ns + '''-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: flux-''' + tenant_ns + '''-role
subjects:
  - kind: ServiceAccount
    name: flux-''' + tenant_ns + '''-sa
    namespace: ''' + tenant_ns)
	s.send('kubectl create -f rbac-config-' + tenant_ns + '.yaml -n ' + tenant_ns)

	# FLUX TENANT RBAC
	# Required to allow fluxctl to work - need to wait for https://github.com/weaveworks/flux/pull/1668 to land to enable whitelisting of namespaces
	s.send_file('rbac-config-' + tenant_ns + '-cluster.yaml','''kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: flux-''' + tenant_ns + '''-cluster-role
rules:
- apiGroups: ["flux.weave.works",""]
  resources: ["*"]
  verbs: ["list", "watch", "get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: flux-''' + tenant_ns + '''-cluster-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: flux-''' + tenant_ns + '''-cluster-role
subjects:
  - kind: ServiceAccount
    name: flux-''' + tenant_ns + '''-sa
    namespace: ''' + tenant_ns)
	s.send('kubectl create -f rbac-config-' + tenant_ns + '-cluster.yaml -n ' + tenant_ns)

	# purge any existing helm reference to flux-tenant from previous runs
	s.send('helm delete --purge flux-' + tenant_ns + ' || true',note='Delete any pre-existing helm install, as per https://github.com/helm/helm/issues/3208')

	# FLUX GLOBAL (installs tenant helm and flux)
	s.send('helm repo add weaveworks https://weaveworks.github.io/flux',note='Add helm repo for flux')
	s.send('kubectl apply -f https://raw.githubusercontent.com/weaveworks/flux/master/deploy-helm/flux-helm-release-crd.yaml',note='create CRD for flux')

	s.send('helm delete --purge flux || true',note='Delete any pre-existing helm install, as per https://github.com/helm/helm/issues/3208')
	s.send('sleep 120',note='Wait until helm ready')
	s.send('helm upgrade -i flux --set image.tag=1.10.0 --set helmOperator.create=true --set helmOperator.createCRD=false --set git.url=git@github.com:ianmiell/flux-get-started --namespace flux weaveworks/flux',note='Initialise flux with the get-started repo')
	s.send('sleep 120',note='Wait until flux ready set up')

	s.send('kubectl -n flux logs deployment/flux',note='Check fluxlogs')
	# Get identity and upload to github
	s.send('fluxctl list-controllers --all-namespaces --k8s-fwd-ns flux',note='List controllers')
	fluxctl_identity = s.send_and_get_output('fluxctl identity --k8s-fwd-ns flux')
	r = g.get_repo("ianmiell/flux-get-started")
	r.create_key('auto-key-' + str(int(time.time())), fluxctl_identity, read_only=False)
	s.send('sleep 60',note='Wait until all set up')
	s.pause_point('is flux ok?')
	s.send('fluxctl sync --k8s-fwd-ns flux')


	# FLUX TENANT
	# Get identity of flux tenant and upload to github
	fluxctl_identity = s.send_and_get_output('fluxctl identity --k8s-fwd-ns ' + tenant_ns)
	r = g.get_repo("ianmiell/flux-get-started-" + tenant_ns)
	r.create_key('auto-key-' + str(int(time.time())), fluxctl_identity, read_only=False)

	s.send('fluxctl list-workloads -a --k8s-fwd-ns flux')
	s.send('fluxctl sync --k8s-fwd-ns tenant')
	s.pause_point('Now flux in ' + tenant_ns + ' ns?')
