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
	s.send('cd shutit_kubernetes')
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
    kubeconfig := "/home/imiell/.kube/config"
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        log.Fatal(err)
    }
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }

    // clientset maps to kubernetes/clientset.go in client-go
    // CoreV1 seems to trace back to: k8s.io/client-go/kubernetes/typed/core/v1, and thence to: kubernetes/typed/core/v1/core_client.go
    // This Interface has a bunch of items in it, eg: PodsGetter
    // type PodsGetter interface {
    //   Pods(namespace string) PodInterface
    // }
    // Pods is back at kubernetes/typed/core/v1/core_client.go where it's implemented (?) and it runs newPods, which is in: kubernetes/typed/core/v1/pod.go
    pods, err := clientset.CoreV1().Pods("").List(metav1.ListOptions{})
    if err != nil {
        panic(err.Error())
    }
    fmt.Printf("There are %d pods in the cluster\n", len(pods.Items))
    for _, pod := range pods.Items {
        fmt.Printf("Pod name %s\n", pod.GetName())
    }
	// TODO: determine how to get a list of daemonsets. This will show how to use a different typed in the client-go kubernetes folder
	// TODO: Miell@Ians-Air-2:/space/git/client-go/kubernetes/typed  ⑂ v9.0.0    vi apps/v1/daemonset.go - is that implemented in core_client.go?
}
END''')
	s.send('go build')
	s.pause_point('shutit_kubernetes')
	s.pause_point('do https://searchitoperations.techtarget.com/tutorial/Follow-a-Kubernetes-and-Go-tutorial-in-your-home-lab')
