# Installs helm and flux for global powers.
# Then uses a helm chart to install helm and flux to a specific namespace.

from github import Github
import os

def do_helm_flux(s):

	__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	f = open(os.path.join(__location__, 'github.key'))
	key = f.read().strip()
	g = Github(key)
	TODO: that api doesnt handle keys - look at github.py
	https://github3.readthedocs.io/en/latest/api-reference/repos.html#repository-objects

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
	s.send('helm upgrade -i flux --set helmOperator.create=true --set helmOperator.createCRD=false --set git.url=git@github.com:ianmiell/flux-get-started --namespace flux weaveworks/flux',note='Initialise flux with the get-started repo')
	s.send('sleep 60',note='Wait until flux ready set up')
	s.send('kubectl -n flux logs deployment/flux',note='Check fluxlogs')
	s.send('export FLUX_FORWARD_NAMESPACE=flux',note='Specify the flux namespace in an env variable')

	# Get identity and upload to github
	s.send('fluxctl list-controllers --all-namespaces',note='List controllers')
	fluxctl_identity = s.send_and_get_output('fluxctl identity')
	r = g.get_repo("ianmiell/flux-get-started")
	r.create_key('auto-key',fluxctl_identity, read_only=False)

	s.send('sleep 60',note='Wait until all set up')

	# FLUX TENANT
	# Now we have helm global, and flux global, we now need to create a flux local in the tenant namespace
	s.send('helm upgrade -i flux-tenant --set helmOperator.create=false --set helmOperator.createCRD=false --set git.url=git@github.com:ianmiell/flux-get-started-tenant --namespace tenant --install weaveworks/flux')
	s.send('sleep 60',note='Wait until all set up')

	# Get identity and upload to github
	fluxctl_identity = s.send_and_get_output('fluxctl identity --k8s-fwd-ns tenant')
	r = g.get_repo("ianmiell/flux-get-started-tenant")
	r.create_key('auto-key',fluxctl_identity, read_only=False)

	s.pause_point('Now flux in tenant ns?')
