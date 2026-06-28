---
title: "4 - Set Limits for Resources in Kubernetes"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

Recently some of the performance issues were observed with some applications hosted on Kubernetes cluster. The Nautilus DevOps team has observed some resources constraints, where some of the applications are running out of resources like memory, cpu etc., and some of the applications are consuming more resources than needed. Therefore, the team has decided to add some limits for resources utilization. Below you can find more details.


Create a pod named httpd-pod and a container under it named as httpd-container, use httpd image with latest tag only and remember to mention tag i.e httpd:latest and set the following limits:

Requests: Memory: 15Mi, CPU: 100m

Limits: Memory: 20Mi, CPU: 100m

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.

CheckCompleteIncomplete

## Solution

```shell
thor@jump_host ~$ k run httpd-pod --image=httpd:latest -o yaml --dry-run=client > po.yml

thor@jump_host ~$ vi po.yml

thor@jump_host ~$ cat po.yml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: httpd-pod
  name: httpd-pod
spec:
  containers:
  - image: httpd:latest
    name: httpd-container
    resources:
      requests:
        cpu: 100m
        memory: 15Mi
      limits:
        cpu: 100m
        memory: 20Mi
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}

thor@jump_host ~$ k apply -f po.yml
pod/httpd-pod created

thor@jump_host ~$ k get po
NAME        READY   STATUS    RESTARTS   AGE
httpd-pod   1/1     Running   0          12s
```
