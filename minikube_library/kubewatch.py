def do_kubewatch(s):
	s.send('''cat > ian-rbac.yaml << END
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: ian-rbac
subjects:
  - kind: ServiceAccount
    # Reference to upper's `metadata.name`
    name: default
    # Reference to upper's `metadata.namespace`
    namespace: default
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
END''')
	s.send('kubectl create -f ian-rbac.yaml')
	s.send('kubectl create -f <(curl -L https://github.com/ianmiell/kubewatch/releases/download/v0.0.3/kubewatch.yaml)')
	s.send('kubectl get pods')
	s.pause_point('')
