---
title: "9 - Countdown job in Kubernetes"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

The Nautilus DevOps team is working on to create few jobs in Kubernetes cluster. They might come up with some real scripts/commands to use, but for now they are preparing the templates and testing the jobs with dummy commands. Please create a job template as per details given below:

Create a job countdown-devops.

The spec template should be named as countdown-devops (under metadata), and the container should be named as container-countdown-devops

Use image debian with latest tag only and remember to mention tag i.e debian:latest, and restart policy should be Never.

Use command sleep 5

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.


## Solution

```yaml
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: countdown-devops
spec:
  template:
    metadata:
      name: countdown-devops
    spec:
      containers:
      - name: container-countdown-devops
        image: debian:latest
        command:
        - /bin/sh
        - -c
        - sleep 5
      restartPolicy: Never
EOF
```
