#!/bin/bash
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
if [[ ! -a "$SHUTIT" ]]
then
	echo "Must have shutit on path, eg export PATH=$PATH:/path/to/shutit_dir"
	exit 1
fi
function usage() {
	cat > /dev/stdout << END
$0 BUILD

Where BUILD is one of:

- basic                    - Sets up a default cluster
- kaniko                   - A demo kaniko build
- knative                  - TODO
- flux                     - TODO
- rook                     - TODO
- admission_controller     - Sets up an admission controller
- client_go                - Builds a basic go client
- istio                    - Follows istio in action book
- operator                 - Builds an operator
- kubebuilder              - Kubebuilder
- concourse                - Deploys concourse CI
- clair                    - Deploys Clair
- jenkinsx                 - Deploys Jenkinsx
- image_policy_webhook     - Deploys ImagePolicyWebhook
- cilium                   - Deploys cilium

END
}
BUILD=$1
shift
if [[ ${BUILD} = 'kaniko' ]]
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
	    -m shutit-library/vagrant \
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'knative' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative yes \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'flux' ]]
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
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'rook' ]]
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
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'admission_controller' ]]
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
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'client_go' ]]
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
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'istio' ]]
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
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'operator' ]]
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
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'kubebuilder' ]]
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
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'concourse' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_concourse yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'clair' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_concourse no \
		-s techniques.shutit_minikube.shutit_minikube do_clair yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'jenkinsx' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_concourse no \
		-s techniques.shutit_minikube.shutit_minikube do_clair no \
		-s techniques.shutit_minikube.shutit_minikube do_jenkinsx yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'grafeas' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_concourse no \
		-s techniques.shutit_minikube.shutit_minikube do_clair no \
		-s techniques.shutit_minikube.shutit_minikube do_jenkinsx no \
		-s techniques.shutit_minikube.shutit_minikube do_grafeas yes \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant \
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'image_policy_webhook' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_concourse no \
		-s techniques.shutit_minikube.shutit_minikube do_clair no \
		-s techniques.shutit_minikube.shutit_minikube do_jenkinsx no \
		-s techniques.shutit_minikube.shutit_minikube do_grafeas no \
		-s techniques.shutit_minikube.shutit_minikube do_image_policy_webhook yes \
		-s techniques.shutit_minikube.shutit_minikube do_cilium no \
		-s techniques.shutit_minikube.shutit_minikube kubernetes_version 'v1.11.3' \
		-m shutit-library/vagrant \
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'cilium' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
		-s techniques.shutit_minikube.shutit_minikube download yes \
		-s techniques.shutit_minikube.shutit_minikube do_knative no \
		-s techniques.shutit_minikube.shutit_minikube do_istio no \
		-s techniques.shutit_minikube.shutit_minikube do_basic no \
		-s techniques.shutit_minikube.shutit_minikube do_kubebuilder no \
		-s techniques.shutit_minikube.shutit_minikube do_concourse no \
		-s techniques.shutit_minikube.shutit_minikube do_clair no \
		-s techniques.shutit_minikube.shutit_minikube do_jenkinsx no \
		-s techniques.shutit_minikube.shutit_minikube do_grafeas no \
		-s techniques.shutit_minikube.shutit_minikube do_image_policy_webhook no \
		-s techniques.shutit_minikube.shutit_minikube do_cilium yes \
		-m shutit-library/vagrant \
		-m shutit-library/virtualization \
		"$@"
elif [[ ${BUILD} = 'basic' ]]
then
	${SHUTIT} build --echo -d bash -m shutit-library/vagrant -m shutit-library/virtualization "$@"
else
	usage
	exit 1
fi
if [[ $? != 0 ]]
then
	exit 1
fi
