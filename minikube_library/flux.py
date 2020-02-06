def do_flux(s, p):
	#https://github.com/weaveworks/flux/blob/master/site/get-started.md
	if not s.command_available('helm'):
		# https://docs.helm.sh/using_helm/#installing-the-helm-client
		s.multisend('curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | sudo bash',{'assword':pw},note='Install helm')
	# Assumes helm is installed and is version 3
	if s.send_and_get_output('helm version --short')[:2] != 'v3':
		s.pause_point('helm v3 should be installed, and is not')
	# fluxctl
	if not s.command_available('fluxctl'):
		s.pause_point('fluxctl not available')
	# create tmp flux folder
	s.send('rm -rf ~/minikube_tmp/flux')
	s.send('mkdir -p ~/minikube_tmp/flux')
	s.send('cd ~/minikube_tmp/flux')

	s.send('helm repo add fluxcd https://charts.fluxcd.io')
	s.send('kubectl create namespace flux')
	# Create FluxHelmRelease CRD
	s.send('kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/master/deploy/flux-helm-release-crd.yaml')
	s.send('helm upgrade -i flux fluxcd/flux --set git.url=git@github.com:ianmiell/flux-get-started --namespace flux')
	s.send('helm upgrade -i helm-operator fluxcd/helm-operator --set git.ssh.secretName=flux-git-deploy --namespace flux')
	s.pause_point('kubectl -n flux get pods')
	##s.send('kubectl -n kube-system create sa tiller',note='Create tiller service account')
	##s.send('kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller',note='Bind admin cluster role to tiller')
	#s.send('helm init --skip-refresh --upgrade --service-account tiller',note='Initialize helm')
	## https://github.com/weaveworks/flux/blob/master/site/helm-get-started.md
	## https://github.com/weaveworks/flux/blob/master/site/fluxctl.md
	#s.send('helm repo add weaveworks https://weaveworks.github.io/flux',note='Add helm repo for flux')
	#s.send('sleep 60',note='Wait until flux ready set up')
	#s.send('kubectl apply -f https://raw.githubusercontent.com/weaveworks/flux/master/deploy-helm/flux-helm-release-crd.yaml',note='create CRD for flux')
	#s.send('sleep 60',note='Wait until flux ready set up')
	#s.send('helm upgrade -i flux --set helmOperator.create=true --set helmOperator.createCRD=false --set git.url=git@github.com:ianmiell/flux-get-started --namespace flux weaveworks/flux',note='Initialise flux with the get-started repo')
	#s.send('kubectl -n flux logs deployment/flux',note='Check fluxlogs')
	#s.send('export FLUX_FORWARD_NAMESPACE=flux',note='Specify the flux namespace in an env variable')
	#s.send('fluxctl list-controllers --all-namespaces',note='List controllers')
	#s.send('fluxctl identity',note='Get the fluxctl public key')
	s.pause_point('add flux shutit key above to github and continue https://github.com/YOURUSER/flux-get-started/settings/keys/new')
	#s.send('kubectl create secret generic flux-git-deploy --from-file /tmp/pubkey -n flux')
	#s.pause_point('Now add the secret to the flux-deployment.yaml manifest')
