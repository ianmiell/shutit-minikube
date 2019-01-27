def do_cilium(s):
	# FROM: https://cilium.readthedocs.io/en/stable/gettingstarted/minikube/
	s.send('kubectl create -n kube-system -f https://raw.githubusercontent.com/cilium/cilium/1.3.2/examples/kubernetes/addons/etcd/standalone-etcd.yaml')
	s.send_until('kubectl get pods -n kube-system | grep -v NAME | grep cilium | wc -l','1')
	s.send_until('kubectl get pods -n kube-system | grep -v NAME | grep -v Running | wc -l','0')
	s.send('kubectl create -f https://raw.githubusercontent.com/cilium/cilium/1.3.2/examples/kubernetes/1.12/cilium.yaml')
	s.send_until("kubectl get daemonsets -n kube-system | grep cilium | awk '{print $3'}",'1')
	s.send('kubectl create -f https://raw.githubusercontent.com/cilium/cilium/1.3.2/examples/minikube/http-sw-app.yaml')
	s.send_until('kubectl exec xwing -- curl -s -XPOST deathstar.default.svc.cluster.local/v1/request-landing','Ship landed')
	s.send_until('kubectl exec tiefighter -- curl -s -XPOST deathstar.default.svc.cluster.local/v1/request-landing','Ship landed')
	s.send('kubectl get pods,svc')
	podname = s.send_and_get_output('kubectl -n kube-system get pods -l k8s-app=cilium | grep cilium | cut -d1')
	s.send('kubectl -n kube-system exec cilium-1c2cz -- cilium endpoint list')
	policy = '''apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
description: "L3-L4 policy to restrict deathstar access to empire ships only"
metadata:
  name: "rule1"
spec:
  endpointSelector:
    matchLabels:
      org: empire
      class: deathstar
  ingress:
  - fromEndpoints:
    - matchLabels:
        org: empire
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP'''
	s.send('kubectl create -f https://raw.githubusercontent.com/cilium/cilium/1.3.2/examples/minikube/sw_l3_l4_policy.yaml')
	s.pause_point('SHOULD HANG: kubectl exec xwing -- curl -s -XPOST deathstar.default.svc.cluster.local/v1/request-landing')

