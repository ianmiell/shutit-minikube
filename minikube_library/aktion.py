def do_aktion(s):
	s.send('go get github.com/triggermesh/aktion')
	s.send('cd ~/go/src/github.com/triggermesh/aktion/')
	s.send('aktion parser -f samples/main.workflow')
	s.send('aktion create -f samples/main.workflow')
	s.send('aktion create -f samples/main.workflow --git https://github.com/sebgoa/klr-demo')
	s.send('aktion create -f samples/main.workflow | kubectl apply -f -')
	s.send('aktion launch --task knative-test --git sebgoa/cloudbuild')
	s.pause_point('')
