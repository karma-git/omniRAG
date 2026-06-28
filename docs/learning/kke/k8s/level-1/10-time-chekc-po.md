---
title: "10 - Kubernetes Time Check Pod"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

The Nautilus DevOps team want to create a time check pod in a particular Kubernetes namespace and record the logs. This might be initially used only for testing purposes, but later can be implemented in an existing cluster. Please find more details below about the task and perform it.


Create a pod called time-check in the nautilus namespace. This pod should run a container called time-check, container should use the busybox image with latest tag only and remember to mention tag i.e busybox:latest.

Create a config map called time-config with the data TIME_FREQ=10 in the same namespace.

The time-check container should run the command: while true; do date; sleep $TIME_FREQ;done and should write the result to the location /opt/finance/time/time-check.log. Remember you will also need to add an environmental variable TIME_FREQ in the container, which should pick value from the config map TIME_FREQ key.

Create a volume log-volume and mount the same on /opt/finance/time within the container.

Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.

## Solution

```yaml
k create ns nautilus
kubectl apply -f - <<EOF
---

apiVersion: v1
kind: ConfigMap
metadata:
  name: time-config
  namespace: nautilus
data:
  TIME_FREQ: "10"

---
apiVersion: v1
kind: Pod
metadata:
  name: time-check
  namespace: nautilus
  labels:
    run: foo
spec:
  volumes:
    - name: log-volume
      emptyDir: {}
  containers:
  - image: busybox:latest
    name: time-check
    resources: {}
    volumeMounts:
      - mountPath: /opt/finance/time
        name: log-volume
    envFrom:
      - configMapRef:
          name: time-config
    command:
      - /bin/sh
      - -c
      - while true; do date; sleep $TIME_FREQ;done > /opt/finance/time/time-check.log
EOF
```
