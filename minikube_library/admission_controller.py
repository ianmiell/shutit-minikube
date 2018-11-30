def do_admission_controller(s):
	# See: https://github.com/jasonrichardsmith/mwcexample
	# See: https://container-solutions.com/some-admission-webhook-basics/
	s.send('rm -rf ~/minikube_tmp/admission_controlller')
	s.send('mkdir -p ~/minikube_tmp/admission_controlller')
	s.send('cd ~/minikube_tmp/admission_controlller')
	s.send('git clone https://github.com/jasonrichardsmith/mwcexample')
	s.send('cd mwcexample')
	s.send('make minikube')
	s.send('make')
	# No need to push as it's to another user's docker repo
	#s.send('make push')
	s.send('kubectl apply -f ns.yaml')
	s.send('./gen-cert.sh')
	s.send('./ca-bundle.sh')
	s.send('kubectl apply -f manifest-ca.yaml')
	s.send('kubectl apply -f test.yaml')
	s.send('kubectl get pods -n mwc-test -o json | jq .items[0].metadata.labels')
	s.pause_point()
