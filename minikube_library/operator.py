
def do_operator(s, pw):
	s.send('cd')
	s.send('rm -rf ~/minikube_tmp/operator')
	s.send('mkdir -p ~/minikube_tmp/operator')
	s.send('')
	# Aim is to automate this rolebinding
	#---
	#kind: RoleBinding
	#apiVersion: rbac.authorization.k8s.io/v1beta1
	#metadata:
	#  name: kubernetes-team-1
	#  namespace: team-1
	#subjects:
	#- kind: Group
	#  name: kubernetes-team-1
	#  apiGroup: rbac.authorization.k8s.io
	#roleRef:
	#  kind: ClusterRole
	#  name: edit
	#  apiGroup: rbac.authorization.k8s.io
	# See also: https://github.com/treacher/namespace-rolebinding-operator
	s.send('cd ~/minikube_tmp/operator')
	s.send('rm -rf cmd')
	s.send('mkdir cmd')
	s.send('cd cmd')
	s.send('''cat > main.go << EOF
package main
import (
	"flag"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"sync"
	"syscall"

	"github.com/treacher/namespace-rolebinding-operator/pkg/controller"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
)
func main() {
	// Set logging output to standard console out
EOF''')
#	log.SetOutput(os.Stdout)
#
#	sigs := make(chan os.Signal, 1) // Create channel to receive OS signals
#	stop := make(chan struct{})     // Create channel to receive stop signal
#
#	signal.Notify(sigs, os.Interrupt, syscall.SIGTERM, syscall.SIGINT) // Register the sigs channel to receieve SIGTERM
#
#	wg := &sync.WaitGroup{} // Goroutines can add themselves to this to be waited on so that they finish
#
#	runOutsideCluster := flag.Bool("run-outside-cluster", false, "Set this flag when running outside of the cluster.")
#	flag.Parse()
#	// Create clientset for interacting with the kubernetes cluster
#	clientset, err := newClientSet(*runOutsideCluster)
#
#	if err != nil {
#		panic(err.Error())
#	}
#
#	controller.NewNamespaceController(clientset).Run(stop, wg)
#
#	<-sigs // Wait for signals (this hangs until a signal arrives)
#	log.Printf("Shutting down...")
#
#	close(stop) // Tell goroutines to stop themselves
#	wg.Wait()   // Wait for all to be stopped
#}
#
#func newClientSet(runOutsideCluster bool) (*kubernetes.Clientset, error) {
#	kubeConfigLocation := ""
#
#	if runOutsideCluster == true {
#		homeDir := os.Getenv("HOME")
#		kubeConfigLocation = filepath.Join(homeDir, ".kube", "config")
#	}
#
#	// use the current context in kubeconfig
#	config, err := clientcmd.BuildConfigFromFlags("", kubeConfigLocation)
#
#	if err != nil {
#		return nil, err
#	}
#
#	return kubernetes.NewForConfig(config)
#}
#EOF''')
	s.send('cd ..')
	s.send('mkdir -p pkg/controller')
	s.send('cd pkg/controller')
	s.send('''cat > controller.go << EOF
package controller
EOF''')
#
#import (
#	"fmt"
#	"log"
#	"sync"
#	"time"
#
#	"k8s.io/api/core/v1"
#	"k8s.io/api/rbac/v1beta1"
#	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
#	"k8s.io/apimachinery/pkg/runtime"
#	"k8s.io/apimachinery/pkg/watch"
#	"k8s.io/client-go/kubernetes"
#	"k8s.io/client-go/tools/cache"
#)
#
#// NamespaceController watches the kubernetes api for changes to namespaces and
#// creates a RoleBinding for that particular namespace.
#type NamespaceController struct {
#	namespaceInformer cache.SharedIndexInformer
#	kclient           *kubernetes.Clientset
#}
#
#// Run starts the process for listening for namespace changes and acting upon those changes.
#func (c *NamespaceController) Run(stopCh <-chan struct{}, wg *sync.WaitGroup) {
#	// When this function completes, mark the go function as done
#	defer wg.Done()
#
#	// Increment wait group as we're about to execute a go function
#	wg.Add(1)
#
#	// Execute go function
#	go c.namespaceInformer.Run(stopCh)
#
#	// Wait till we receive a stop signal
#	<-stopCh
#}
#
#// NewNamespaceController creates a new NewNamespaceController
#func NewNamespaceController(kclient *kubernetes.Clientset) *NamespaceController {
#	namespaceWatcher := &NamespaceController{}
#
#	// Create informer for watching Namespaces
#	namespaceInformer := cache.NewSharedIndexInformer(
#		&cache.ListWatch{
#			ListFunc: func(options metav1.ListOptions) (runtime.Object, error) {
#				return kclient.Core().Namespaces().List(options)
#			},
#			WatchFunc: func(options metav1.ListOptions) (watch.Interface, error) {
#				return kclient.Core().Namespaces().Watch(options)
#			},
#		},
#		&v1.Namespace{},
#		3*time.Minute,
#		cache.Indexers{cache.NamespaceIndex: cache.MetaNamespaceIndexFunc},
#	)
#
#	namespaceInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
#		AddFunc: namespaceWatcher.createRoleBinding,
#	})
#
#	namespaceWatcher.kclient = kclient
#	namespaceWatcher.namespaceInformer = namespaceInformer
#
#	return namespaceWatcher
#}
#
#func (c *NamespaceController) createRoleBinding(obj interface{}) {
#	namespaceObj := obj.(*v1.Namespace)
#	namespaceName := namespaceObj.Name
#
#	roleBinding := &v1beta1.RoleBinding{
#		TypeMeta: metav1.TypeMeta{
#			Kind:       "RoleBinding",
#			APIVersion: "rbac.authorization.k8s.io/v1beta1",
#		},
#		ObjectMeta: metav1.ObjectMeta{
#			Name:      fmt.Sprintf("ad-kubernetes-%s", namespaceName),
#			Namespace: namespaceName,
#		},
#		Subjects: []v1beta1.Subject{
#			v1beta1.Subject{
#				Kind: "Group",
#				Name: fmt.Sprintf("ad-kubernetes-%s", namespaceName),
#			},
#		},
#		RoleRef: v1beta1.RoleRef{
#			APIGroup: "rbac.authorization.k8s.io",
#			Kind:     "ClusterRole",
#			Name:     "edit",
#		},
#	}
#
#	_, err := c.kclient.Rbac().RoleBindings(namespaceName).Create(roleBinding)
#
#	if err != nil {
#		log.Println(fmt.Sprintf("Failed to create Role Binding: %s", err.Error()))
#	} else {
#		log.Println(fmt.Sprintf("Created AD RoleBinding for Namespace: %s", roleBinding.Name))
#	}
#}
#EOF''')
	s.send('cd ../..')
	s.send('''cat > Makefile << 'EOF'
OPERATOR_NAME  := namespace-rolebinding-operator
VERSION := $(shell date +%Y%m%d%H%M)
IMAGE := treacher/$(OPERATOR_NAME)

.PHONY: install_deps build build-image

install_deps:
	glide install

build:
	rm -rf bin/%/$(OPERATOR_NAME)
	go build -v -i -o bin/$(OPERATOR_NAME) ./cmd

bin/%/$(OPERATOR_NAME):
	rm -rf bin/%/$(OPERATOR_NAME)
	GOOS=$* GOARCH=amd64 go build -v -i -o bin/$*/$(OPERATOR_NAME) ./cmd

build-image: bin/linux/$(OPERATOR_NAME)
	docker build . -t $(IMAGE):$(VERSION)
EOF''')
	s.send('make install_deps')
	s.send('make build')
	s.send('./bin/namespace-rolebinding-operator --run-outside-cluster 1')

	s.pause_point('https://medium.com/@mtreacher/writing-a-kubernetes-operator-a9b86f19bfb9')
