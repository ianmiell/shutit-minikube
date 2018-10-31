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
$SHUTIT build --echo -d bash -s techniques.shutit_minikube.shutit_minikube download yes -s techniques.shutit_minikube.shutit_minikube do_istio yes -m shutit-library/vagrant -m shutit-library/virtualization "$@"
if [[ $? != 0 ]]
then
	exit 1
fi
