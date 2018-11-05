def do_client_go(s, kubernetes_version):
	# https://searchitoperations.techtarget.com/tutorial/Follow-a-Kubernetes-and-Go-tutorial-in-your-home-lab
	if kubernetes_version == '1.10.0':
		gopkg_tml = '''[[constraint]]
  name = "k8s.io/api"
  version = "kubernetes-''' + kubernetes_version + '''"
[[constraint]]
  name = "k8s.io/apimachinery"
  version = "kubernetes-''' + kubernetes_version + '''"
[[constraint]]
  name = "k8s.io/client-go"
  version = "7.0.0"'''
	else:
		s.pause_point('kubeversion not handled')
	s.send('''cat > Gopkg.toml << END
''' + gopkg_tml + '''
END''')
	s.install('go-dep')
	s.send('go get k8s.io/client-go/...')
	s.send('cd ${GOPATH}/src')
	s.send('dep init shutit_kubernetes')
	s.send(r'''cat > k.go << END
package main

import (
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/client-go/kubernetes"
    "log"
    "fmt"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func main() {
    kubeconfig = "/home/imiell/.kube/config"
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        log.Fatal(err)
    }
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    pods, err := clientset.CoreV1().Pods("").List(metav1.ListOptions{})
    if err != nil {
        panic(err.Error())
    }
    fmt.Printf("There are %d pods in the cluster\n", len(pods.Items))
    for _, pod := range pods.Items {
        fmt.Printf("Pod name %s\n", pod.GetName())
    }
}
END''')
	s.send('go build')
	s.pause_point('shutit_kubernetes')
	s.pause_point('do https://searchitoperations.techtarget.com/tutorial/Follow-a-Kubernetes-and-Go-tutorial-in-your-home-lab')
