# update based on your IBM Container Registry namespace
NAMESPACE=<YOUR_CONTAINER_REGISTRY>

# update based on your Ingress Subdomain (use `ibmcloud ks cluster get --cluster <CLUSTERNAME>` to obtain)
INGRESSSUBDOMAIN=jpetstore.<YOUR_INGRESS_SUBDOMAIN>

# the IBM container registry
REGISTRY=us.icr.io

TIMESTAMP="$(shell date)"

build-petstore:
	cd jpetstore && docker build . -t $(REGISTRY)/$(NAMESPACE)/jpetstoreweb
	docker push $(REGISTRY)/$(NAMESPACE)/jpetstoreweb
	cd jpetstore/db && docker build . -t $(REGISTRY)/$(NAMESPACE)/jpetstoredb
	docker push $(REGISTRY)/$(NAMESPACE)/jpetstoredb

deploy-using-helm:
	cd helm && helm install --name jpetstore ./modernpets

remove-deployments:
	helm delete jpetstore --purge

remove-images:
	ibmcloud cr image-rm $(REGISTRY)/$(NAMESPACE)/jpetstoredb
	ibmcloud cr image-rm $(REGISTRY)/$(NAMESPACE)/jpetstoreweb





