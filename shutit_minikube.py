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
from minikube_library import rook
from minikube_library import kaniko
from minikube_library import helm
from minikube_library import concourse
from minikube_library import clair
from minikube_library import jenkinsx
from minikube_library import grafeas
from minikube_library import image_policy_webhook
from minikube_library import flux

class shutit_minikube(ShutItModule):


	def do_rbac(self, shutit):
		# Need RBAC
		shutit.send('minikube start --extra-config=apiserver.authorization-mode=RBAC --memory=4096')
		shutit.send('kubectl create clusterrolebinding add-on-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:default')

	def create_pv(self, shutit):
		# cf: https://github.com/kubernetes/minikube/blob/master/docs/persistent_volumes.md
		shutit.send_file('pv.yaml','''apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 5Gi
  hostPath:
    path: /data/pv0001/''')
		shutit.send('kubectl create -f pv.yaml')
		shutit.send('rm pv.yaml')

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
			shutit.send('chmod +x $HOME/bin/kubectl')
			# Windows
			#curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/windows/amd64/kubectl.exe
			if OS == 'Linux':
				shutit.send('curl https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 > $HOME/bin/minikube')
			elif OS == 'Darwin':
				shutit.send('curl https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64 > $HOME/bin/minikube')
			shutit.send('chmod +x $HOME/bin/minikube')
		shutit.send('export PATH=$(pwd):${PATH}')
		shutit.send('minikube delete || true')
		shutit.send('minikube config set WantKubectlDownloadMsg false')
		if shutit.cfg[self.module_id]['do_client_go']:
			shutit.send('minikube start --kubernetes-version=v' + shutit.cfg[self.module_id]['kubernetes_version'])
			client_go.do_client_go(shutit,  shutit.cfg[self.module_id]['kubernetes_version'])
		elif shutit.cfg[self.module_id]['do_istio']:
			shutit.send('minikube start --memory=4096 --disk-size=30g --kubernetes-version=v' + shutit.cfg[self.module_id]['kubernetes_version'])
			istio.do_istio(shutit, shutit.cfg[self.module_id]['istio_version'])
			istio.do_istioinaction(shutit)
		elif shutit.cfg[self.module_id]['do_knative']:
			shutit.send('minikube start --memory=8192 --cpus=4 --disk-size=30g --kubernetes-version=' + shutit.cfg[self.module_id]['kubernetes_version'] + ' --bootstrapper=kubeadm --extra-config=apiserver.enable-admission-plugins="LimitRanger,NamespaceExists,NamespaceLifecycle,ResourceQuota,ServiceAccount,DefaultStorageClass,MutatingAdmissionWebhook"')
			knative.do_knative(shutit)
		elif shutit.cfg[self.module_id]['do_kubebuilder']:
			shutit.send('minikube start')
			kubebuilder.do_kubebuilder(shutit,pw)
		elif shutit.cfg[self.module_id]['do_operator']:
			shutit.send('minikube start')
			operator.do_operator(shutit,pw)
		elif shutit.cfg[self.module_id]['do_flux']:
			shutit.send('minikube start')
			flux.do_flux(shutit)
		elif shutit.cfg[self.module_id]['do_kaniko']:
			shutit.send('minikube start')
			# Blows up?
			shutit.get_config(self.module_id,'docker_username')
			shutit.get_config(self.module_id,'docker_server')
			shutit.get_config(self.module_id,'docker_password')
			shutit.get_config(self.module_id,'docker_email')
			kaniko.do_kaniko(shutit, shutit.cfg[self.module_id]['docker_username'], shutit.cfg[self.module_id]['docker_server'], shutit.cfg[self.module_id]['docker_password'], shutit.cfg[self.module_id]['docker_email'])
		elif shutit.cfg[self.module_id]['do_admission_controller']:
			shutit.send('minikube start')
			admission_controller.do_admission_controller_opa(shutit)
			# Does not work
			#admission_controller.do_admission_controller_validating(shutit)
			admission_controller.do_admission_controller_mutating(shutit)
		elif shutit.cfg[self.module_id]['do_rook']:
			shutit.send('minikube start')
			rook.do_rook(shutit)
		elif shutit.cfg[self.module_id]['do_concourse']:
			self.do_rbac(shutit)
			# Needs helm
			helm.do_helm(shutit)
			concourse.do_concourse(shutit)
		elif shutit.cfg[self.module_id]['do_clair']:
			self.do_rbac(shutit)
			# Needs helm
			helm.do_helm(shutit)
			clair.do_clair(shutit)
		elif shutit.cfg[self.module_id]['do_jenkinsx']:
			self.do_rbac(shutit)
			helm.do_helm(shutit)
			self.create_pv(shutit)
			jenkinsx.do_jenkinsx(shutit)
		elif shutit.cfg[self.module_id]['do_grafeas']:
			shutit.send('minikube start')
			grafeas.do_grafeas(shutit)
		elif shutit.cfg[self.module_id]['do_image_policy_webhook']:
			shutit.send('minikube start')
			image_policy_webhook.do_image_policy_webhook(shutit)
		elif shutit.cfg[self.module_id]['do_basic']:
			shutit.send('minikube start')
			shutit.send('kubectl run hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080')
			shutit.send('kubectl expose deployment hello-minikube --type=NodePort')
			shutit.send('kubectl get pod')
			shutit.send('curl $(minikube service hello-minikube --url)')
		else:
			shutit.pause_point('No do_ACTION chosen?')
		shutit.pause_point('all done')
		return True


	def get_config(self, shutit):
		for do in ('basic', 'istio', 'knative', 'client_go','kubebuilder','flux','operator','admission_controller','rook','kaniko','concourse','clair','jenkinsx','grafeas','image_policy_webhook'):
			shutit.get_config(self.module_id,'do_' + do,boolean=True,default=False)
		shutit.get_config(self.module_id,'istio_version',default='1.0.3')
		shutit.get_config(self.module_id,'kubernetes_version',default='1.12.0')
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
