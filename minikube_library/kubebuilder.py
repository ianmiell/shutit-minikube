
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
	s.send('kubebuilder init')
	s.send('kubebuilder create api')
	s.pause_point('https://book.kubebuilder.io/getting_started/hello_world.html')
