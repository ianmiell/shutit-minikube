
def do_kubebuilder(s, pw):
	s.send('cd')
	s.send('version=1.0.5')
	s.send('arch=amd64')
	# Linux
	os = s.send_and_get_output('uname')
	if os == 'Darwin':
		os = 'darwin'
	elif os == 'Linux':
		os = 'linux'
	s.send('os=' + os)
	s.send('curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v${version}/kubebuilder_${version}_${os}_${arch}.tar.gz')
	s.send('tar -zxvf kubebuilder_${version}_${os}_${arch}.tar.gz')
	s.multisend('sudo rm -rf /usr/local/kubebuilder',{'assword':pw})
	s.multisend('sudo mv kubebuilder_${version}_${os}_${arch} /usr/local/kubebuilder',{'assword':pw})
	s.send('export PATH=$PATH:/usr/local/kubebuilder/bin')
	s.send('rm -rf ~/go/src/kubebuilder_egtmp')
	s.send('mkdir -p ~/go/src/kubebuilder_egtmp')
	s.send('cd ~/go/src/kubebuilder_egtmp')
	# See also: https://book.kubebuilder.io/basics/project_creation_and_structure.html
	s.multisend('kubebuilder init',{'ecommended':'y'})
	s.multisend('kubebuilder create api --group workloads --version v1beta1 --kind ContainerSet',{'Create':'y'})
	s.send('env | grep PATH')
	s.pause_point('https://book.kubebuilder.io/getting_started/hello_world.html')
