def do_flux(shutit):
	#https://github.com/weaveworks/flux/blob/master/site/get-started.md
	s.send('rm -rf ~/minikube_tmp/flux')
	s.send('mkdir -p ~/minikube_tmp/flux')
	s.send('cd ~/minikube_tmp/flux')
	s.send('git clone https://github.com/weaveworks/flux')
	s.send('cd flux')
	s.pause_point('''go to: Now you can go ahead and edit Flux's deployment manifest. At the very least you will have to change the --git-url parameter to point to the config repository for the workloads you want Flux to deploy for you. You are going to need access to this repository.''')
