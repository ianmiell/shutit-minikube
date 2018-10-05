def do_kubewatch(s):
	s.send('wget https://github.com/skippbox/kubewatch/releases/download/v0.0.3/kubewatch.yaml')
	s.send('kubectl create -f kubewatch.yaml')
	s.send('kubectl get pods')
	s.pause_point('')
