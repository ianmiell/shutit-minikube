def do_kaniko(s, docker_username, docker_server, docker_password, docker_email):
	s.send('rm -rf kaniko_tmp')
	s.send('mkdir -p kaniko_tmp')
	s.send('cd kaniko_tmp')
	s.send('touch kaniko-secret.json')
	s.send('kubectl create secret docker-registry docker-secret --docker-server=' + docker_server + ' --docker-username=' + docker_username + ' --docker-password=' + docker_password + ' --docker-email=' + docker_email)
	s.send_file('''kaniko.yaml''','''apiVersion: batch/v1
kind: Job
metadata:
  name: kanikojob
  namespace: default
spec:
  completions: 1
  template:
    metadata:
      name: kanikojob
      namespace: default
    spec:
      restartPolicy: Never
      initContainers:
      - name: init-clone-repo
        image: alpine/git
        args:
            - clone
            - --single-branch
            - --
            - https://github.com/ianmiell/simple-dockerfile.git
            - /context
        volumeMounts:
        - name: context
          mountPath: /context
      containers:
      - name: kaniko
        image: gcr.io/kaniko-project/executor:latest
        args: ["--dockerfile=/context/Dockerfile",
              "--context=/context",
              "--destination=docker.io/imiell/simple-dockerfile:latest"]
        volumeMounts:
          - name: context
            mountPath: /context
          - name:  registry-creds
            mountPath: /root/
      volumes:
        - name: registry-creds
          projected:
            sources:
            - secret:
                name: docker-secret
                items:
                - key: .dockerconfigjson
                  path: .docker/config.json
        - name: context
          emptyDir: {}''')
	s.send('kubectl create -f kaniko.yaml')
	s.pause_point('TODO remove pass!')
