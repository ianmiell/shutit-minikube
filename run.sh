#!/bin/bash
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
if [[ ! -a "$SHUTIT" ]]
then
	echo "Must have shutit on path, eg export PATH=$PATH:/path/to/shutit_dir"
	exit 1
fi
if [[ $1 = 'kaniko' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
	    -s techniques.shutit_minikube.shutit_minikube download yes \
	    -s techniques.shutit_minikube.shutit_minikube do_knative no \
	    -s techniques.shutit_minikube.shutit_minikube do_istio no \
	    -s techniques.shutit_minikube.shutit_minikube do_basic no \
	    -s techniques.shutit_minikube.shutit_minikube do_flux no \
	    -s techniques.shutit_minikube.shutit_minikube do_kaniko yes \
	    -s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
	    -m shutit-library/vagrant -m shutit-library/virtualization "$@"
elif [[ $1 = 'knative' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative yes \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant -m shutit-library/virtualization "$@"
elif [[ $1 = 'flux' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_flux yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant -m shutit-library/virtualization "$@"
elif [[ $1 = 'rook' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build -d bash \
		-w \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_admission_controller no \
		-s techniques.shutit_minikube.shutit_minikube do_rook yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.12.0' \
		-m shutit-library/vagrant -m shutit-library/virtualization "$@"
elif [[ $1 = 'admission_controller' ]]
then
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
elif [[ $1 = 'client_go' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_client_go yes \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version '1.10.0' \
		-m shutit-library/vagrant -m shutit-library/virtualization "$@"
elif [[ $1 = 'istio' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-w \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio yes \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version '1.10.0' \
		-m shutit-library/vagrant -m shutit-library/virtualization "$@"
elif [[ $1 = 'operator' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_operator yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant -m shutit-library/virtualization "$@"
elif [[ $1 = 'kubebuilder' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant -m shutit-library/virtualization "$@"
else
	$SHUTIT build --echo -d bash -m shutit-library/vagrant -m shutit-library/virtualization "$@"
fi
if [[ $? != 0 ]]
then
	exit 1
fi
