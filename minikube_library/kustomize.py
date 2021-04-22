def do_kustomize(s):
	s.send('curl -s "https://raw.githubusercontent.com/ kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash')
	s.pause_point('kustomize')
