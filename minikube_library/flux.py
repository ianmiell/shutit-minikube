def do_flux(s, pw):
	#https://github.com/weaveworks/flux/blob/master/site/get-started.md
	s.send('rm -rf ~/minikube_tmp/flux')
	s.send('mkdir -p ~/minikube_tmp/flux')
	s.send('cd ~/minikube_tmp/flux')
	#s.send('git clone https://github.com/weaveworks/flux')
	#s.send('cd flux')
	#s.pause_point('''go to: Now you can go ahead and edit Flux's deployment manifest. At the very least you will have to change the --git-url parameter to point to the config repository for the workloads you want Flux to deploy for you. You are going to need access to this repository.''')
	s.send('wget https://github.com/weaveworks/flux/releases/download/1.9.0/fluxctl_linux_amd64')
	s.send('chmod +x fluxctl_linux_amd64')
	s.send('mv fluxctl_linux_amd64 fluxctl')
	if not s.command_available('helm'):
		# https://docs.helm.sh/using_helm/#installing-the-helm-client
		s.multisend('curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | sudo bash',{'assword':pw})
	# https://github.com/weaveworks/flux/blob/master/site/helm-get-started.md
	# https://github.com/weaveworks/flux/blob/master/site/fluxctl.md
	s.send('kubectl -n kube-system create sa tiller')
	s.send('kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller')
	s.send('helm init --skip-refresh --upgrade --service-account tiller')
	s.send('helm repo add weaveworks https://weaveworks.github.io/flux')
	s.send('kubectl apply -f https://raw.githubusercontent.com/weaveworks/flux/master/deploy-helm/flux-helm-release-crd.yaml')
	s.send('helm upgrade -i flux --set helmOperator.create=true --set helmOperator.createCRD=false --set git.url=git@github.com:imiell/flux-get-started --namespace flux weaveworks/flux')
	s.send('export FLUX_FORWARD_NAMESPACE=flux')
	s.send('fluxctl identity')
	s.pause_point('add flux shutit key above to github and continue https://github.com/YOURUSER/flux-get-started/settings/keys/new')
	#s.send('kubectl create secret generic flux-git-deploy --from-file /tmp/pubkey -n flux')
	#s.pause_point('Now add the secret to the flux-deployment.yaml manifest')
