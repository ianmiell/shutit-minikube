# TODO

def do_istio(s):
	s.send('cd')
	s.send('rm -rf istiominikube')
	s.send('mkdir -p istiominikube')
	s.send('cd istiominikube')
	s.send('curl -L https://git.io/getLatestIstio | sh -')
	s.send('cd istio-1.0.2')
	s.send('export PATH=$PWD/bin:$PATH')
	s.send('kubectl apply -f install/kubernetes/helm/istio/templates/crds.yaml')
	s.send('kubectl apply -f install/kubernetes/istio-demo-auth.yaml')
	s.send('kubectl get svc -n istio-system')
	s.send('kubectl get pods -n istio-system')
	s.pause_point('')
