# TODO

def do_istio(s):
	s.send('rm -rf istiotmp')
	s.send('mkdir -p istiotmp')
	s.send('cd istiotmp')
	OS = s.send_and_get_output('uname')
	if OS == 'Linux':
		s.send('wget -qO- https://github.com/istio/istio/releases/download/1.0.3/istio-1.0.3-linux.tar.gz | tar -zxvf -')
	elif OS == 'Darwin':
		s.send('wget -qO- https://github.com/istio/istio/releases/download/1.0.3/istio-1.0.3-osx.tar.gz | tar -zxvf -')
	s.send('cd istio-1.0.3')
	s.send('./bin/istioctl version')
	s.send('kubectl create -f install/kubernetes/istio-demo.yaml')
	s.pause_point('p39')
