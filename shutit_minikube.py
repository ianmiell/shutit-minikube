import random
import logging
import string
import os
import inspect
from shutit_module import ShutItModule
from minikube_library import kubewatch
from minikube_library import istio
from minikube_library import knative
from minikube_library import client_go
from minikube_library import kubebuilder
from minikube_library import operator
from minikube_library import admission_controller

class shutit_minikube(ShutItModule):


	def build(self, shutit):
		################################################################################
		# Extract password from 'secret' file (which git ignores).
		# TODO: check perms are only readable by user
		try:
		    pw = open('secret').read().strip()
		except IOError:
		    pw = ''
		if pw == '':
		    shutit.log('''================================================================================\nWARNING! IF THIS DOES NOT WORK YOU MAY NEED TO SET UP A 'secret' FILE IN THIS FOLDER!\n================================================================================''',level=logging.CRITICAL)
		    pw='nopass'

		# ASSUMING LINUX FOR NOW
		# OS X
		# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl
		# Linux
		OS = shutit.send_and_get_output('uname')
		shutit.send('mkdir -p ~/bin')
		if shutit.cfg[self.module_id]['download']:
			if OS == 'Linux':
				shutit.send('curl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl > ~/bin/kubectl')
			elif OS == 'Darwin':
				shutit.send('curl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl > ~/bin/kubectl')
			shutit.send('chmod +x ~/bin/kubectl')
			# Windows
			#curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/windows/amd64/kubectl.exe
			if OS == 'Linux':
				shutit.send('curl https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 > ~/bin/minikube')
			elif OS == 'Darwin':
				shutit.send('curl https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64 > ~/bin/minikube')
			shutit.send('chmod +x ~/bin/minikube')
		shutit.send('export PATH=$(pwd):${PATH}')
		shutit.send('minikube delete || true')
		shutit.send('minikube config set WantKubectlDownloadMsg false')
		if shutit.cfg[self.module_id]['do_client_go']:
			shutit.send('minikube start --kubernetes-version=v' + shutit.cfg[self.module_id]['kubernetes_version'])
			client_go.do_client_go(shutit,  shutit.cfg[self.module_id]['kubernetes_version'])
		if shutit.cfg[self.module_id]['do_istio']:
			shutit.send('minikube start --memory=4096 --disk-size=30g --kubernetes-version=v' + shutit.cfg[self.module_id]['kubernetes_version'])
			istio.do_istio(shutit, shutit.cfg[self.module_id]['istio_version'])
			istio.do_istioinaction(shutit)
		if shutit.cfg[self.module_id]['do_knative']:
			shutit.send('minikube start --memory=8192 --cpus=4 --disk-size=30g --kubernetes-version=' + shutit.cfg[self.module_id]['kubernetes_version'] + ' --bootstrapper=kubeadm --extra-config=apiserver.enable-admission-plugins="LimitRanger,NamespaceExists,NamespaceLifecycle,ResourceQuota,ServiceAccount,DefaultStorageClass,MutatingAdmissionWebhook"')
			knative.do_knative(shutit)
		if shutit.cfg[self.module_id]['do_kubebuilder']:
			shutit.send('minikube start')
			kubebuilder.do_kubebuilder(shutit,pw)
		if shutit.cfg[self.module_id]['do_operator']:
			shutit.send('minikube start')
			operator.do_operator(shutit,pw)
		if shutit.cfg[self.module_id]['do_flux']:
			shutit.send('minikube start')
			flux.do_flux(shutit)
		if shutit.cfg[self.module_id]['do_admission_controller']:
			shutit.send('minikube start')
			admission_controller.do_admission_controller(shutit)
		if shutit.cfg[self.module_id]['do_basic']:
			shutit.send('minikube start')
			shutit.send('kubectl run hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080')
			shutit.send('kubectl expose deployment hello-minikube --type=NodePort')
			shutit.send('kubectl get pod')
			shutit.send('curl $(minikube service hello-minikube --url)')

		shutit.pause_point('done')
		return True


	def get_config(self, shutit):
		shutit.get_config(self.module_id,'do_basic',boolean=True,default=True)
		shutit.get_config(self.module_id,'do_istio',boolean=True,default=False)
		shutit.get_config(self.module_id,'do_knative',boolean=True,default=False)
		shutit.get_config(self.module_id,'do_client_go',boolean=True,default=False)
		shutit.get_config(self.module_id,'do_kubebuilder',boolean=True,default=False)
		shutit.get_config(self.module_id,'do_flux',boolean=True,default=False)
		shutit.get_config(self.module_id,'do_operator',boolean=True,default=False)
		shutit.get_config(self.module_id,'do_admission_controller',boolean=True,default=False)
		shutit.get_config(self.module_id,'istio_version',default='1.0.3')
		shutit.get_config(self.module_id,'kubernetes_version',default='1.11.0')
		shutit.get_config(self.module_id,'download',default=True,boolean=True)
		return True

def module():
	return shutit_minikube(
		'techniques.shutit_minikube.shutit_minikube', 2135119025.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization']
	)
