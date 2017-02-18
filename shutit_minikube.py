import random
import logging
import string
import os
import inspect
from shutit_module import ShutItModule

class shutit_minikube(ShutItModule):


	def build(self, shutit):
		# https://kubernetes.io/docs/user-guide/prereqs/

		# ASSUMING LINUX FOR NOW
		# OS X
		# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl
		# Linux
		shutit.send('curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl')
		shutit.send('chmod +x kubectl')
		shutit.send('cp kubectl /usr/local/bin/kubectl')
		# Windows
		#curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/windows/amd64/kubectl.exe
		shutit.send('curl https://storage.googleapis.com/minikube/releases/v0.16.0/minikube-linux-amd64 > minikube')
		shutit.send('chmod +x minikube')
		shutit.send('./minikube start')
		shutit.send('kubectl run hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080')
		shutit.send('kubectl expose deployment hello-minikube --type=NodePort')
		shutit.send('kubectl get pod')
		shutit.send('curl $(minikube service hello-minikube --url)')
		shutit.pause_point('')
		return True


	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/xenial64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='1024')
		shutit.get_config(self.module_id,'vagrant_run_dir',default='/tmp')
		shutit.get_config(self.module_id,'this_vagrant_run_dir',default='/tmp')
		return True

	def test(self, shutit):
		return True

	def finalize(self, shutit):
		return True

	def is_installed(self, shutit):
		# Destroy pre-existing, leftover vagrant images.
		shutit.run_script('''#!/bin/bash
MODULE_NAME=shutit_minikube
rm -rf $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/vagrant_run/*
if [[ $(command -v VBoxManage) != '' ]]
then
	while true
	do
		VBoxManage list runningvms | grep ${MODULE_NAME} | awk '{print $1}' | xargs -IXXX VBoxManage controlvm 'XXX' poweroff && VBoxManage list vms | grep shutit_minikube | awk '{print $1}'  | xargs -IXXX VBoxManage unregistervm 'XXX' --delete
		# The xargs removes whitespace
		if [[ $(VBoxManage list vms | grep ${MODULE_NAME} | wc -l | xargs) -eq '0' ]]
		then
			break
		else
			ps -ef | grep virtualbox | grep ${MODULE_NAME} | awk '{print $2}' | xargs kill
			sleep 10
		fi
	done
fi
if [[ $(command -v virsh) ]] && [[ $(kvm-ok 2>&1 | command grep 'can be used') != '' ]]
then
	virsh list | grep ${MODULE_NAME} | awk '{print $1}' | xargs -n1 virsh destroy
fi
''')
		return False

	def start(self, shutit):
		return True

	def stop(self, shutit):
		return True

def module():
	return shutit_minikube(
		'techniques.shutit_minikube.shutit_minikube', 2135119025.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization']
	)
