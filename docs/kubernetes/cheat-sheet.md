---
title: "Kubernetes Cheat Sheet"
tags:
  - k8s
  - cheatsheet
---

# Kubernetes Cheat Sheet

**Как узнать mode kubeproxy?**

```shell
# выполним http get запрос на worker Node
[root@ip-10-110-38-206 /]# curl localhost:10249/proxyMode
ipvs
```
