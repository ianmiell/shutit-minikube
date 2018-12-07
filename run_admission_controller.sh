#!/bin/bash
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
if [[ ! -a "$SHUTIT" ]]
then
	echo "Must have shutit on path, eg export PATH=$PATH:/path/to/shutit_dir"
	echo "shutit is a pip install"
	exit 1
fi
git submodule init
git submodule update
$SHUTIT build -d bash \
	-w \
	-s techniques.shutit_minikube.shutit_minikube download yes \
	-s techniques.shutit_minikube.shutit_minikube do_knative no \
	-s techniques.shutit_minikube.shutit_minikube do_istio no \
	-s techniques.shutit_minikube.shutit_minikube do_basic no \
	-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
	-s techniques.shutit_minikube.shutit_minikube do_admission_controller yes \
	-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.12.0' \
	-m shutit-library/vagrant -m shutit-library/virtualization "$@"
if [[ $? != 0 ]]
then
	exit 1
fi
