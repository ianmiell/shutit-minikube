import random
import logging
import string
import os
import inspect
from shutit_module import ShutItModule
from minikube_library import kubewatch
from minikube_library import istio

class shutit_minikube(ShutItModule):


	def build(self, shutit):
		# https://kubernetes.io/docs/user-guide/prereqs/

		# ASSUMING LINUX FOR NOW
		# OS X
		# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl
		# Linux
		OS = shutit.send_and_get_output('uname')
		if OS == 'Linux':
			shutit.send('curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl')
		elif OS == 'Darwin':
			shutit.send('curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl')
		shutit.send('chmod +x kubectl')
		# Windows
		#curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/windows/amd64/kubectl.exe
		if OS == 'Linux':
			shutit.send('curl https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 > minikube')
		elif OS == 'Darwin':
			shutit.send('curl https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64 > minikube')
		shutit.send('chmod +x minikube')
		shutit.send('./minikube delete || true')
		shutit.send('./minikube config set WantKubectlDownloadMsg false')
		if shutit.cfg[self.module_id]['do_istio']:
			shutit.send('./minikube start --memory=4096 --disk-size=30g --kubernetes-version=' + shutit.cfg[self.module_id]['kubernetes_version'])
			shutit.send('export PATH=$(pwd):${PATH}')
			istio.do_istio(shutit, shutit.cfg[self.module_id]['istio_version'])
		else:
			shutit.send('./minikube start')
			shutit.send('./kubectl run hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080')
			shutit.send('./kubectl expose deployment hello-minikube --type=NodePort')
			shutit.send('./kubectl get pod')
			shutit.send('curl $(./minikube service hello-minikube --url)')
			shutit.send('export PATH=.:${PATH}')
			shutit.send('curl $(./minikube service hello-minikube --url)')

		shutit.pause_point('done')
		return True


	def get_config(self, shutit):
		shutit.get_config(self.module_id,'do_istio',boolean=True,default=False)
		shutit.get_config(self.module_id,'istio_version',default='1.0.3')
		shutit.get_config(self.module_id,'kubernetes_version',default='v1.10.0')
		return True

def module():
	return shutit_minikube(
		'techniques.shutit_minikube.shutit_minikube', 2135119025.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization']
	)
