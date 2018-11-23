
def do_kubebuilder(s):
	s.send('cd')
	s.send('mkdir -p kubebuilder')
	s.send('cd kubebuilder')
	s.send('version=1.0.5')
	s.send('arch=amd64')
	s.send('curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v${version}/kubebuilder_${version}_darwin_${arch}.tar.gz')
	s.send('tar -zxvf kubebuilder_${version}_darwin_${arch}.tar.gz')
	# TODO: darwin?
	s.send('mv kubebuilder_${version}_darwin_${arch} kubebuilder')
	s.send('export PATH=$PATH:$(pwd)')
	s.send('rm -rf $GOPATH/src/kubebuilder_egtmp')
	s.send('mkdir -p $GOPATH/src/kubebuilder_egtmp')
	s.send('cd $GOPATH/src/kubebuilder_egtmp')
	# See also: https://book.kubebuilder.io/basics/project_creation_and_structure.html
	s.multisend('kubebuilder init',{'ecommended':'y'})
	s.multisend('kubebuilder create api --group workloads --version v1beta1 --kind ContainerSet',{'Create':'y'})
	s.pause_point('https://book.kubebuilder.io/getting_started/hello_world.html')
