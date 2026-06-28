---
title: "1 - Create Pods in Kubernetes Cluster"
tags:
  - kodekloud-engineer-kubernetes
---

## Task


The Nautilus DevOps team has started practicing some pods and services deployment on Kubernetes platform as they are planning to migrate most of their applications on Kubernetes platform. Recently one of the team members has been assigned a task to create a pod as per details mentioned below:


Create a pod named pod-httpd using httpd image with latest tag only and remember to mention the tag i.e httpd:latest.

Labels app should be set to httpd_app, also container should be named as httpd-container.

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.

CheckCompleteIncomplete


## Solution

```shell
thor@jump_host ~$ k run pod-httpd --image httpd:latest --labels="app=httpd_app" --dry-run=client -o yaml > po.yml
# change containers[0].name  pod-httpd -> httpd-container
thor@jump_host ~$ vi po.yml
thor@jump_host ~$ k apply -f po.yml 
pod/pod-httpd created
# wait until Pod will be in running state
k get po --watch
```
