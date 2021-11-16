# Payload web app
Create a web app to upload data under certain requirements

This is a simple web app that will get you going while using the minimum resources required to run on a K8S cluster.

tools used:
- python flask REST API server
- mysql
- docker
- minikube
- postman

## Part 1 - The web app

Write a web service in any language that takes in a JSON payload, does
some basic validation against an expected message format and content,
and then puts that payload into a queue of your choice, in this case MySQL server.

Example valid payload:

```
{
  "ts": "1530228282",
  "sender": "testy-test-service",
  "message": {
    "foo": "bar",
    "baz": "bang"
  },
  "sent-from-ip": "1.2.3.4",
  "priority": 2
}
```

Validation rules:
- “ts” must be present and a valid Unix timestamp
- “sender” must be present and a string
- “message” must be present, a JSON object, and have at least one
field set
- If present, “sent-from-ip” must be a valid IPv4 address
- All fields not listed in the example above are invalid, and
should result in the message being rejected.

## Part 2 - Dockerize it

Write a Dockerfile to produce a container that will run the service, and one to spin up an
instance of the queue you used in Part 1.

## Part 3 - Kubefy it

Write Kubernetes manifests to create a Service and Deployment object for both your service
and the queue.


# Run the app !!

## Pre-requsites

Prerequisites: Have kubectland minikube installed (https://kubernetes.io/docs/tasks/tools/). And make sure your Docker CLI uses the Docker deamon in your cluster via the command:  
`$ eval $(minikube docker-env)`  
After this is done, start your cluster:  
`$ minikube start`

## The app development and containerization

The development of the has has been built up to preference and organised in way that is clear to understand.  
The packages used for the app are defined in the requirements.txt file and a simple python image as been used from dockerhub.  
`$ docker build -t payloadimg:latest .`

## Create secrets

Needed to configure the credentials to access the database.  
remember to use base64-encoded string:  
`$ echo -n <super-secret-passwod> | base64`  
and add it to the root password in the data section.

Use the secrets.yaml file  
`$ kubectl apply -f secrets.yaml`

## Create persistent volume

Persistent volume is needed for the database so that data is not lost in case the nodes go down.

In this case, a hostPath type will be used. It creates a volume on your minikube node. Use another type in a production environment as data will be lost if you delete your minikube node when using a hostPath type.

Making an application use a persistent volume consists of two parts:

1. Specifying the actual storage type, location, size and properties of the volume.
2. Specify a persistent volume claim that requests a specific size and access modes of the persistent volume for your deployments. 

Use the secrets.yaml file  
`$ kubectl apply -f persistent-volume.yaml`

Confirm th creation of the persist volume by running
```
$ kubectl describe pv mysql-pv-volume
$ kubectl describe pvc mysql-pv-claim
```

As hostPath is the type for the persistent volume, you can find the data by logging into the minikube node `$ minikube ssh` and navigate to the spcified path (/mnt/data).

## Deploy MySQL server

Pull the latest mysql image `$ docker pull mysql`

Use the mysql-deployment.yaml file  
`$ kubectl apply -f mysql-deployment.yaml`

the DB and Table is created when requesting the app. No need to create manually.

## Create a deployment

imagePullPolicy is to never to make sure the locally built image is used.

Use the deployment.yaml file  
`$ kubectl apply -f deployment.yaml`

## Run and test the REST API server

Run the following command to start the service:  
`$ minikube start payload-web-service`

This will give you an IP from which you can access your service.


## Upload data

In this case I used postman for convenience, make sure the type of date to be uploaded is set to json and you should get response from your REST API server.  
Alternatively curl can also be used:
`$ curl -H "Content-Type: application/json" -d '{
  "ts": "1530228282",
  "sender": "testy-test-service",
  "message": {
    "foo": "bar",
    "baz": "bang"
  },
  "sent-from-ip": "1.2.3.4",
  "priority": 2
}'`

## Confirm your data is stored in the DB

This can be possible by launching a temporary client pod on the cluster by running the following:  
`$ kubectl run -it --rm --image=mysql:latest --restart=Never mysql-client -- mysql --host mysql --password=<your-password>`

After it you should get regular mysql prompt and run regular mysql commands.

# Voila

Thanks
