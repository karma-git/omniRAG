---
title: "2 - Create Deployments in Kubernetes Cluster"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

The Nautilus DevOps team has started practicing some pods, and services deployment on Kubernetes platform, as they are planning to migrate most of their applications on Kubernetes. Recently one of the team members has been assigned a task to create a deployment as per details mentioned below:

Create a deployment named httpd to deploy the application httpd using the image httpd:latest (remember to mention the tag as well)

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.

## Solution

```shell
thor@jump_host ~$ k create deploy httpd --image=httpd:latest
deployment.apps/httpd created
thor@jump_host ~$ k get deploy
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
httpd   1/1     1            1           13s
```
