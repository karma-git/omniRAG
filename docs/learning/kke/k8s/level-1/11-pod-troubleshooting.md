---
title: "11 - Troubleshoot Issue With Pods"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

One of the junior DevOps team members was working on to deploy a stack on Kubernetes cluster. Somehow the pod is not coming up and its failing with some errors. We need to fix this as soon as possible. Please look into it.


There is a pod named webserver and the container under it is named as httpd-container. It is using image httpd:latest

There is a sidecar container as well named sidecar-container which is using ubuntu:latest image.

Look into the issue and fix it, make sure pod is in running state and you are able to access the app.

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.


## Solution

```shell
thor@jump_host ~$ k describe po webserver
Name:             webserver
...
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Pulling    19s (x3 over 62s)  kubelet            Pulling image "httpd:latests"
  Warning  Failed     19s (x3 over 62s)  kubelet            Failed to pull image "httpd:latests": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/httpd:latests": failed to resolve reference "docker.io/library/httpd:latests": docker.io/library/httpd:latests: not found
  Warning  Failed     19s (x3 over 62s)  kubelet            Error: ErrImagePull
...

# NOTE: Change `httpd:latests` -> `httpd:latest` from plural to singular
thor@jump_host ~$ k edit pod webserver
pod/webserver edited
thor@jump_host ~$ k get po
NAME        READY   STATUS    RESTARTS   AGE
webserver   2/2     Running   0          5m37s
```
