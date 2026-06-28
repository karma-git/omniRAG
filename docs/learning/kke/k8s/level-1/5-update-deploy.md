---
id: 5-update-deploy
title: "5 - Rolling Updates in Kubernetes"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

We have an application running on Kubernetes cluster using nginx web server. The Nautilus application development team has pushed some of the latest changes and those changes need be deployed. The Nautilus DevOps team has created an image nginx:1.19 with the latest changes.


Perform a rolling update for this application and incorporate nginx:1.19 image. The deployment name is nginx-deployment

Make sure all pods are up and running after the update.

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.

CheckCompleteIncomplete


## Solution

```shell
thor@jump_host ~$ k describe deploy nginx-deployment
Name:                   nginx-deployment
Namespace:              default
CreationTimestamp:      Mon, 14 Aug 2023 06:36:01 +0000
Labels:                 app=nginx-app
                        type=front-end
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=nginx-app
Replicas:               3 desired | 3 updated | 3 total | 3 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=nginx-app
  Containers:
   nginx-container:
    Image:        nginx:1.16
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  <none>
NewReplicaSet:   nginx-deployment-989f57c54 (3/3 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  78s   deployment-controller  Scaled up replica set nginx-deployment-989f57c54 to 3

# kubectl set image deployment/frontend www=image:v2               # Rolling update "www" containers of "frontend" deployment, updating the image
thor@jump_host ~$ kubectl set image deployment/nginx-deployment  nginx-container=nginx:1.19
deployment.apps/nginx-deployment image updated

thor@jump_host ~$ k get po
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-dc49f85cc-ffq48   1/1     Running   0          7s
nginx-deployment-dc49f85cc-xb554   1/1     Running   0          21s
nginx-deployment-dc49f85cc-xdsxf   1/1     Running   0          10s
```
