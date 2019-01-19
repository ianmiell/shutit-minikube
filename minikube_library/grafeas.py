import random
import shutit
def do_grafeas(s):
	s.send('rm -rf tmp_grafeas')
	s.send('mkdir -p tmp_grafeas/gnupg')
	s.send('cd tmp_grafeas')
	s.send('export GNUPGHOME=$(pwd)/gnupg')
	s.send('git clone https://github.com/kelseyhightower/grafeas-tutorial.git')
	s.send('cd grafeas-tutorial/pki')
	s.send_file('gen_certs.sh','''#!/bin/bash
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=10.0.2.15,127.0.0.1,image-signature-webhook,image-signature-webhook.kube-system,image-signature-webhook.default,image-signature-webhook.default.svc -profile=default image-signature-webhook-csr.json | cfssljson -bare image-signature-webhook
kubectl create secret tls tls-image-signature-webhook --cert=image-signature-webhook.pem --key=image-signature-webhook-key.pem''')
	s.send('chmod +x gen_certs.sh')
	s.send('./gen_certs.sh')
	s.send('cd ..')
	s.send('kubectl apply -f kubernetes/grafeas.yaml')
	# TODO: linux too, as per: https://github.com/kelseyhightower/grafeas-tutorial.git README
	OS = 'Darwin'
	if OS == 'Darwin':
		s.send('brew install gpg2')
	rndnum = str(int(random.random() * 999999))
	s.send("gpg --batch --passphrase '' --quick-generate-key --yes grafeas-" + rndnum + "-image.signer@example.com")
	s.send(r'''gpg --list-keys --keyid-format short''')
	keyid = s.send_and_get_output(r'''gpg --list-keys --keyid-format short 2>/dev/null | grep ^pub | sed 's/.*rsa2048.\([^ ]*\).*/\1/' ''')
	s.send('GPG_KEY_ID=' + keyid)
	s.send('gpg --armor --export grafeas-' + rndnum + '-image.signer@example.com > ${GPG_KEY_ID}.pub')
	# In this tutorial the gcr.io/hightowerlabs/echod container image will be used for testing. Instead of trusting an image tag such 0.0.1, which can be reused and point to a different container image later, we are going to trust the image digest.
	s.send('cat image-digest.txt')
	s.send('gpg -u grafeas-' + rndnum + '-image.signer@example.com --armor --clearsign --output=signature.gpg image-digest.txt',note='sign the image')
	s.send('gpg --output - --verify signature.gpg',note='verify the signature')
	s.send('gpg --armor --export grafeas-' + rndnum + '-image.signer@example.com > ${GPG_KEY_ID}.pub',note='export the signer public key')
	s.pause_point('ready?')
	d = s.send_and_get_output('pwd')
	# https://github.com/kelseyhightower/grafeas-tutorial#create-a-pgpsignedattestation-occurrence
	# new terminal - is this necessary?
	s2 = shutit.create_session(session_type='bash',loglevel='debug')
	s2.send('cd ' + d)
	s2.send('''kubectl port-forward $(kubectl get pods -l app=grafeas -o jsonpath='{.items[0].metadata.name}') 8080:8080''', expect='Forwarding from')
	s.send('''curl -X POST "http://127.0.0.1:8080/v1alpha1/projects/image-signing/notes?noteId=production" -d @note.json''',note='Create the production attestationAuthority note')
	s.send('GPG_SIGNATURE=$(cat signature.gpg | base64)',note='create the occurrence')
	s.send('RESOURCE_URL="https://gcr.io/hightowerlabs/echod@sha256:aba48d60ba4410ec921f9d2e8169236c57660d121f9430dc9758d754eec8f887"',note='create the occurrence')
	s.send('''cat > occurrence.json <<EOF
{
  "resourceUrl": "${RESOURCE_URL}",
  "noteName": "projects/image-signing/notes/production",
  "attestation": {
    "pgpSignedAttestation": {
       "signature": "${GPG_SIGNATURE}",
       "contentType": "application/vnd.gcr.image.url.v1",
       "pgpKeyId": "${GPG_KEY_ID}"
    }
  }
}
EOF''',note='create the occurrence')
	s.send('''curl -X POST 'http://127.0.0.1:8080/v1alpha1/projects/image-signing/occurrences' -d @occurrence.json''',note='Post the pgpSignedAttestation occurrence')
	s.send('kubectl create configmap image-signature-webhook --from-file ${GPG_KEY_ID}.pub')
	s.send('kubectl get configmap image-signature-webhook -o yaml')
	s.send('kubectl create secret tls tls-image-signature-webhook --key pki/image-signature-webhook-key.pem --cert pki/image-signature-webhook.pem')
	s.pause_point('secret created ok?')
	s.send('kubectl apply -f kubernetes/image-signature-webhook.yaml')
	s.send('kubectl apply -f kubernetes/validating-webhook-configuration.yaml')
	s.pause_point('kubectl get all until ready')
	s.send('kubectl apply -f pods/nginx.yaml', note='No attestation - should fail')
	s.send('kubectl apply -f pods/echod.yaml', note='Attestation exists - should succeed')

	s.pause_point('')
