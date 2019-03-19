# Installs helm and flux for global powers.
# Then uses a helm chart to install helm and flux to a specific namespace.

from github import Github
import os
import time

def do_helm_flux(s):

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

	# FLUX GLOBAL
	s.send('helm repo add weaveworks https://weaveworks.github.io/flux',note='Add helm repo for flux')
	s.send('kubectl apply -f https://raw.githubusercontent.com/weaveworks/flux/master/deploy-helm/flux-helm-release-crd.yaml',note='create CRD for flux')
	s.send('sleep 60',note='Wait until flux ready set up')
	s.send('helm delete --purge flux || true',note='Delete any pre-existing helm install, as per https://github.com/helm/helm/issues/3208')
	s.send('helm upgrade -i flux --set helmOperator.create=true --set helmOperator.createCRD=false --set git.url=git@github.com:ianmiell/flux-get-started --namespace flux weaveworks/flux',note='Initialise flux with the get-started repo')
	s.send('sleep 60',note='Wait until flux ready set up')
	s.send('kubectl -n flux logs deployment/flux',note='Check fluxlogs')
	#s.send('export FLUX_FORWARD_NAMESPACE=flux',note='Specify the flux namespace in an env variable')

	# Get identity and upload to github
	s.send('fluxctl list-controllers --all-namespaces --k8s-fwd-ns flux',note='List controllers')
	fluxctl_identity = s.send_and_get_output('fluxctl identity --k8s-fwd-ns flux')
	r = g.get_repo("ianmiell/flux-get-started")
	r.create_key('auto-key-' + str(int(time.time())), fluxctl_identity, read_only=False)

	s.send('sleep 60',note='Wait until all set up')

	# FLUX TENANT
	# Now we have helm global, and flux global, we now need to create a flux local in the tenant namespace
	# Set up rbac appropriately, bound to the namespace where appropriate.



	s.send_file('rbac-config-tenant.yaml','''kind: Role
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: flux-tenant-role
  namespace: tenant
rules:
- apiGroups: ["", "extensions", "apps", "flux.weave.works"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: flux-tenant-sa
  namespace: tenant
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: flux-tenant-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: flux-tenant-role
subjects:
  - kind: ServiceAccount
    name: flux-tenant-sa
    namespace: tenant''')
	s.send('kubectl create -f rbac-config-tenant.yaml -n tenant')


	s.send_file('rbac-config-tenant-cluster.yaml','''kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: flux-tenant-cluster-role
rules:
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get","list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: flux-tenant-cluster-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: flux-tenant-cluster-role
subjects:
  - kind: ServiceAccount
    name: flux-tenant-sa
    namespace: tenant''')
	s.send('kubectl create -f rbac-config-tenant-cluster.yaml -n tenant')

	# purge any existing helm reference to flux-tenant
	s.send('helm delete --purge flux-tenant || true',note='Delete any pre-existing helm install, as per https://github.com/helm/helm/issues/3208')
	# install the flux-tenant
	# don't create rbac (that sets up a cluster role)
	# set the tiller namespace
	# create a helm operator
	# don't create CRD (that was done by the global flux)
	# set the url appropriately
	s.send(r'''helm upgrade -i flux-tenant \
	         --set rbac.create=false \
	         --set helmOperator.tillerNamespace=tenant \
	         --set helmOperator.create=true \
	         --set helmOperator.createCRD=false \
	         --set serviceAccount.create=false \
	         --set serviceAccount.name=flux-tenant-sa \
	         --set git.url=git@github.com:ianmiell/flux-get-started-tenant \
	         --namespace tenant \
	         --install weaveworks/flux''')
	s.send('sleep 60',note='Wait until all set up')

	# Get identity of flux tenant and upload to github
	fluxctl_identity = s.send_and_get_output('fluxctl identity --k8s-fwd-ns tenant')
	r = g.get_repo("ianmiell/flux-get-started-tenant")
	r.create_key('auto-key-' + str(int(time.time())), fluxctl_identity, read_only=False)

	s.pause_point('Now flux in tenant ns?')

