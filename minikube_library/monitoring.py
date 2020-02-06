def do_monitoring(s):
	# Assumes helm is installed and is version 3
	if s.send_and_get_output('helm version --short')[:2] != 'v3':
		s.pause_point('helm v3 should be installed, and is not')
	# Doesn't seem to work?
	s.send('cd')
	s.send('cd git/charts')
	s.send('helm repo add stable https://kubernetes-charts.storage.googleapis.com/')
	s.send('helm repo update')
	s.send('cd /tmp')
	# From: https://istio.io/docs/setup/getting-started/#download
	s.send('curl -L https://istio.io/downloadIstio | sh -')
	s.send('cd istio-1.4.3')
	s.send('export PATH=$PWD/bin:$PATH')
	s.send('istioctl manifest apply --set profile=demo')
	s.send('kubectl create namespace application')
	#eg kubectl expose deployment hello-minikube --type=NodePort
	s.send('kubectl create deployment hello-node --image=gcr.io/hello-minikube-zero-install/hello-node')
	s.send('kubectl port-forward svc/kiali 20001:20001 -n istio-system')
	s.pause_point('monitoring stuff')
	pass
