import random
import logging
import string
import os
import inspect
import datetime
from shutit_module import ShutItModule
from minikube_library import kubewatch
from minikube_library import kustomize
from minikube_library import istio
from minikube_library import knative
from minikube_library import client_go
from minikube_library import kubebuilder
from minikube_library import operator
from minikube_library import admission_controller
from minikube_library import rook
from minikube_library import kaniko
from minikube_library import helm
from minikube_library import helm_flux
from minikube_library import concourse
from minikube_library import clair
from minikube_library import jenkinsx
from minikube_library import grafeas
from minikube_library import image_policy_webhook
from minikube_library import flux
from minikube_library import cilium
from minikube_library import aktion
from minikube_library import tekton
from minikube_library import trow
from minikube_library import monitoring

class shutit_minikube(ShutItModule):


	def do_rbac(self, shutit):
		vm_provider = shutit.cfg[self.module_id]['vm_provider']
		# Need RBAC
		shutit.send('minikube start -p ' + profile + ' --vm-driver=' + vm_provider + ' --extra-config=apiserver.authorization-mode=RBAC --memory=4096')
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
		kubernetes_version = shutit.cfg[self.module_id]['kubernetes_version']
		vm_provider        = shutit.cfg[self.module_id]['vm_provider']
		profile = datetime.datetime.now().strftime('%Y%m%d%s')
		################################################################################
		# Extract password from 'secret' file (which git ignores).
		# TODO: check perms are only readable by user
		try:
		    pw = open('secret').read().strip()
		except IOError:
		    pw = ''
		if pw == '':
		    shutit.log('''================================================================================\nWARNING! IF THIS DOES NOT WORK YOU MAY NEED TO SET UP A 'secret' FILE IN THIS FOLDER!\n================================================================================''', level=logging.CRITICAL)
		    pw='nopass'

		# ASSUMING LINUX FOR NOW
		# OS X
		# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl
		# Linux
		OS = shutit.send_and_get_output('uname')
		shutit.send('mkdir -p $HOME/bin')
		if shutit.cfg[self.module_id]['download'] or not shutit.command_available('kubectl') or not shutit.command_available('minikube'):
			if OS == 'Linux':
				shutit.send('curl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl > $HOME/bin/kubectl')
			elif OS == 'Darwin':
				shutit.send('curl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl > $HOME/bin/kubectl')
			shutit.send('chmod +x $HOME/bin/kubectl')
			# Windows
			#curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/windows/amd64/kubectl.exe
			if OS == 'Linux':
				shutit.send('curl https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 > $HOME/bin/minikube')
			elif OS == 'Darwin':
				shutit.send('brew cask install minikube')
			shutit.send('chmod +x $HOME/bin/minikube')
		shutit.send('export PATH=$(pwd):${PATH}')
		shutit.send('minikube -p ' + profile + ' delete || true')
		shutit.send('minikube -p ' + profile + ' config set WantKubectlDownloadMsg false')
		if shutit.cfg[self.module_id]['do_client_go']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider + ' --kubernetes-version=v' + kubernetes_version)
			client_go.do_client_go(shutit, kubernetes_version)
		if shutit.cfg[self.module_id]['do_istio']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider + ' --memory=4096 --disk-size=30g --kubernetes-version=v' + kubernetes_version)
			istio.do_istio(shutit, shutit.cfg[self.module_id]['istio_version'])
			istio.do_istioinaction(shutit)
		if shutit.cfg[self.module_id]['do_knative'] or shutit.cfg[self.module_id]['do_aktion']:
			shutit.send('''minikube -p ''' + profile + ''' start --vm-driver=''' + vm_provider + ''' --memory=24576 --cpus=6 --kubernetes-version=v1.12.7 --disk-size=30g --extra-config=apiserver.enable-admission-plugins="LimitRanger,NamespaceExists,NamespaceLifecycle,ResourceQuota,ServiceAccount,DefaultStorageClass,MutatingAdmissionWebhook"''')
			knative.do_knative(shutit)
		if shutit.cfg[self.module_id]['do_aktion']:
			tekton.do_tekton(shutit)
			aktion.do_aktion(shutit)
		if shutit.cfg[self.module_id]['do_tekton']:
			tekton.do_tekton(shutit)
		if shutit.cfg[self.module_id]['do_helm']:
			self.do_rbac(shutit)
			helm.do_helm(shutit)
		if shutit.cfg[self.module_id]['do_trow']:
			self.do_rbac(shutit)
			trow.do_trow(shutit, profile, pw)
		if shutit.cfg[self.module_id]['do_concourse']:
			self.do_rbac(shutit)
			# Needs helm
			helm.do_helm(shutit)
			concourse.do_concourse(shutit)
		if shutit.cfg[self.module_id]['do_clair']:
			self.do_rbac(shutit)
			# Needs helm
			helm.do_helm(shutit)
			clair.do_clair(shutit)
		if shutit.cfg[self.module_id]['do_jenkinsx']:
			self.do_rbac(shutit)
			helm.do_helm(shutit)
			self.create_pv(shutit)
			jenkinsx.do_jenkinsx(shutit)
		if shutit.cfg[self.module_id]['do_grafeas']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			grafeas.do_grafeas(shutit)
		elif shutit.cfg[self.module_id]['do_image_policy_webhook']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			image_policy_webhook.do_image_policy_webhook(shutit)
		elif shutit.cfg[self.module_id]['do_cilium']:
			#shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider + ' --kubernetes-version=v1.12.0 --network-plugin=cni --extra-config=kubelet.network-plugin=cni --memory=5120')
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider + ' --kubernetes-version=v1.12.0  --memory=5120')
			cilium.do_cilium(shutit)
		elif shutit.cfg[self.module_id]['do_basic']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			shutit.send('kubectl run hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080')
			shutit.send('kubectl expose deployment hello-minikube --type=NodePort')
			shutit.send('kubectl get pod')
			shutit.send('curl $(minikube -p ' + profile + ' service hello-minikube --url)')
		elif shutit.cfg[self.module_id]['do_helm_flux']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider + ' --memory=8096')
			shutit.send('kubectl create clusterrolebinding add-on-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:default')
			helm_flux.do_helm_flux(shutit)
		elif shutit.cfg[self.module_id]['do_kustomize']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider + ' --memory=4096 --disk-size=30g --kubernetes-version=v' + kubernetes_version)
			kustomize.do_kustomize(shutit)
		elif shutit.cfg[self.module_id]['do_rook']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			rook.do_rook(shutit)
		elif shutit.cfg[self.module_id]['do_kubebuilder']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			kubebuilder.do_kubebuilder(shutit, pw)
		elif shutit.cfg[self.module_id]['do_operator']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			operator.do_operator(shutit, pw)
		elif shutit.cfg[self.module_id]['do_flux']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			flux.do_flux(shutit, pw)
		elif shutit.cfg[self.module_id]['do_kaniko']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			# Blows up?
			shutit.get_config(self.module_id,'docker_username')
			shutit.get_config(self.module_id,'docker_server')
			shutit.get_config(self.module_id,'docker_password')
			shutit.get_config(self.module_id,'docker_email')
			kaniko.do_kaniko(shutit, shutit.cfg[self.module_id]['docker_username'], shutit.cfg[self.module_id]['docker_server'], shutit.cfg[self.module_id]['docker_password'], shutit.cfg[self.module_id]['docker_email'])
		elif shutit.cfg[self.module_id]['do_admission_controller']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			admission_controller.do_admission_controller_opa(shutit)
			# Does not work
			#admission_controller.do_admission_controller_validating(shutit)
			admission_controller.do_admission_controller_mutating(shutit)
		elif shutit.cfg[self.module_id]['do_monitoring']:
			shutit.send('minikube -p ' + profile + ' start --vm-driver=' + vm_provider)
			# We assume helm is there
			#helm.do_helm(shutit)
			kustomize.do_kustomize(shutit)
			monitoring.do_monitoring(shutit)
		shutit.pause_point('''

Build complete. To set up your env, run:

    minikube profile ''' + profile + '''

Use your VM provider: ''' + vm_provider + '''
to manage the VM.

If you use the VM provider to suspend or shutdown the machine, restart it, and then run:

	minikube start

to get the service back up.

Hit CTRL-] to continue to completion.
''')
		return True


	def get_config(self, shutit):
		for do in ('basic',
		           'istio',
		           'knative',
		           'aktion',
		           'tekton',
		           'client_go',
		           'kubebuilder',
		           'flux',
		           'operator',
		           'admission_controller',
		           'rook',
		           'kaniko',
		           'concourse',
		           'clair',
		           'jenkinsx',
		           'grafeas',
		           'image_policy_webhook',
		           'cilium',
		           'helm',
		           'helm_flux',
		           'trow',
		           'monitoring',
		           'kustomize'):
			shutit.get_config(self.module_id,'do_' + do, boolean=True, default=False)
		shutit.get_config(self.module_id,'istio_version', default='1.0.3')
		shutit.get_config(self.module_id,'kubernetes_version', default='1.17.0')
		shutit.get_config(self.module_id,'download', default=False, boolean=True)
		shutit.get_config(self.module_id,'vm_provider', default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='true')
		return True

def module():
	return shutit_minikube(
		'techniques.shutit_minikube.shutit_minikube', 2135119025.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization']
	)
