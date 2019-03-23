def do_tekton(s):
	s.send('kubectl apply --filename https://storage.googleapis.com/knative-releases/build-pipeline/latest/release.yaml')
	s.send_until('kubectl get pod -n tekton-pipelines | grep -v ^NAME | grep -v Running | wc -l','0',cadence=20)
