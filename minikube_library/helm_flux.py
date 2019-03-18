# Installs helm and flux for global powers.
# Then uses a helm chart to install helm and flux to a specific namespace.

def do_helm_flux(s):
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
	# Flux global
	s.send('helm repo add weaveworks https://weaveworks.github.io/flux',note='Add helm repo for flux')
	s.send('kubectl apply -f https://raw.githubusercontent.com/weaveworks/flux/master/deploy-helm/flux-helm-release-crd.yaml',note='create CRD for flux')
	s.send('sleep 60',note='Wait until flux ready set up')
	s.send('helm upgrade -i flux --set helmOperator.create=true --set helmOperator.createCRD=false --set git.url=git@github.com:ianmiell/flux-get-started --namespace flux weaveworks/flux',note='Initialise flux with the get-started repo')
	s.send('sleep 60',note='Wait until flux ready set up')
	s.send('kubectl -n flux logs deployment/flux',note='Check fluxlogs')
	s.send('export FLUX_FORWARD_NAMESPACE=flux',note='Specify the flux namespace in an env variable')
	s.send('fluxctl list-controllers --all-namespaces',note='List controllers')
	fluxctl_identity = s.send_and_get_output('fluxctl identity')
	s.send('fluxctl identity',note='Get the fluxctl public key')
	# TODO: automate via github api
	s.pause_point('add flux shutit key above to github and continue https://github.com/ianmiell/flux-get-started/settings/keys/new')
	s.pause_point('Now wait for everything in that repo to deploy')
