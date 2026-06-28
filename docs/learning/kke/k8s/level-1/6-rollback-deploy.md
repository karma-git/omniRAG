---
title: "6 - Rollback a Deployment in Kubernetes"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

This morning the Nautilus DevOps team rolled out a new release for one of the applications. Recently one of the customers logged a complaint which seems to be about a bug related to the recent release. Therefore, the team wants to rollback the recent release.


There is a deployment named nginx-deployment; roll it back to the previous revision.

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.


## Solution

```shell
thor@jump_host ~$ k rollout history deploy nginx-deployment
deployment.apps/nginx-deployment 
REVISION  CHANGE-CAUSE
1         <none>
2         kubectl set image deployment nginx-deployment nginx-container=nginx:alpine-perl --kubeconfig=/root/.kube/config --record=true

thor@jump_host ~$ k describe deploy nginx-deployment | grep -i image
                          kubectl set image deployment nginx-deployment nginx-container=nginx:alpine-perl --kubeconfig=/root/.kube/config --record=true
    Image:        nginx:alpine-perl
thor@jump_host ~$ k rollout undo deploy nginx-deployment
deployment.apps/nginx-deployment rolled back
thor@jump_host ~$ k get po
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-989f57c54-fsdql   1/1     Running   0          12s
nginx-deployment-989f57c54-nz5th   1/1     Running   0          10s
nginx-deployment-989f57c54-x7z7d   1/1     Running   0          6s
thor@jump_host ~$ k describe deploy nginx-deployment | grep -i image
    Image:        nginx:1.16
```
