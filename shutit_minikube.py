import random
import logging
import string
import os
import inspect
from shutit_module import ShutItModule

class shutit_minikube(ShutItModule):


	def build(self, shutit):
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
		shutit.cfg[self.module_id]['vagrant_run_dir'] = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0))) + '/vagrant_run'
		run_dir = shutit.cfg[self.module_id]['vagrant_run_dir']
		module_name = 'shutit_minikube_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		this_vagrant_run_dir = run_dir + '/' + module_name
		shutit.cfg[self.module_id]['this_vagrant_run_dir'] = this_vagrant_run_dir
		shutit.send(' command rm -rf ' + this_vagrant_run_dir + ' && command mkdir -p ' + this_vagrant_run_dir + ' && command cd ' + this_vagrant_run_dir)
		shutit.send('command rm -rf ' + this_vagrant_run_dir + ' && command mkdir -p ' + this_vagrant_run_dir + ' && command cd ' + this_vagrant_run_dir)
		if shutit.send_and_get_output('vagrant plugin list | grep landrush') == '':
			shutit.send('vagrant plugin install landrush')
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file(this_vagrant_run_dir + '/Vagrantfile','''Vagrant.configure("2") do |config|
  config.landrush.enabled = true
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
  end

  config.vm.define "minikube1" do |minikube1|
    minikube1.vm.box = ''' + '"' + vagrant_image + '"' + '''
    minikube1.vm.hostname = "minikube1.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_minikube_1"
    end
  end
end''')
		pw = shutit.get_env_pass()
		try:
			shutit.multisend('vagrant up --provider ' + shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] + " minikube1",{'assword for':pw,'assword:':pw},timeout=99999)
		except NameError:
			shutit.multisend('vagrant up minikube1',{'assword for':pw,'assword:':pw},timeout=99999)
		if shutit.send_and_get_output("""vagrant status | grep -w ^minikube1 | awk '{print $2}'""") != 'running':
			shutit.pause_point("machine: minikube1 appears not to have come up cleanly")


		# machines is a dict of dicts containing information about each machine for you to use.
		machines = {}
		machines.update({'minikube1':{'fqdn':'minikube1.vagrant.test'}})
		ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines['minikube1']['fqdn'] + ''' | awk '{print $2}' ''')
		machines.get('minikube1').update({'ip':ip})

		for machine in sorted(machines.keys()):
			shutit.login(command='vagrant ssh ' + machine)
			shutit.login(command='sudo su -',password='vagrant')
			root_password = 'root'
			shutit.install('net-tools') # netstat needed
			if not shutit.command_available('host'):
				shutit.install('bind-utils') # host needed
			# Workaround for docker networking issues + landrush.
			shutit.install('docker')
			shutit.insert_text('Environment=GODEBUG=netdns=cgo','/lib/systemd/system/docker.service',pattern='.Service.')
			shutit.send('mkdir -p /etc/docker',note='Create the docker config folder')
			shutit.send_file('/etc/docker/daemon.json',"""{
  "dns": ["8.8.8.8"]
}""",note='Use the google dns server rather than the vagrant one. Change to the value you want if this does not work, eg if google dns is blocked.')
			shutit.send('systemctl restart docker')
			shutit.multisend('passwd',{'assword:':root_password})
			shutit.send("""sed -i 's/.*PermitRootLogin.*/PermitRootLogin yes/g' /etc/ssh/sshd_config""")
			shutit.send("""sed -i 's/.*PasswordAuthentication.*/PasswordAuthentication yes/g' /etc/ssh/sshd_config""")
			shutit.send('service ssh restart || systemctl restart sshd')
			shutit.multisend('ssh-keygen',{'Enter':'','verwrite':'n'})
			shutit.logout()
			shutit.logout()
		for machine in sorted(machines.keys()):
			shutit.login(command='vagrant ssh ' + machine)
			shutit.login(command='sudo su -',password='vagrant')
			for copy_to_machine in machines:
				for item in ('fqdn','ip'):
					shutit.multisend('ssh-copy-id root@' + machines[copy_to_machine][item],{'assword:':root_password,'ontinue conn':'yes'})
			shutit.logout()
			shutit.logout()
		shutit.login(command='vagrant ssh ' + sorted(machines.keys())[0])
		shutit.login(command='sudo su -',password='vagrant')
		shutit.send('curl https://storage.googleapis.com/minikube/releases/v0.16.0/minikube-linux-amd64 > minikube')
		shutit.send('chmod +x minikube')
		shutit.pause_point('')
		shutit.logout()
		shutit.logout()
		shutit.log('''Vagrantfile created in: ''' + this_vagrant_run_dir,add_final_message=True,level=logging.DEBUG)
		shutit.log('''Run:

	cd ''' + this_vagrant_run_dir + ''' && vagrant status && vagrant landrush ls

To get a picture of what has been set up.''',add_final_message=True,level=logging.DEBUG)
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
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)
