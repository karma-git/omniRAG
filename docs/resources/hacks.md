---
title: "hacks"
tags:
  - hacks
  - tools
  - cheatsheet
---

# hacks

## Kubernetes

### kail (logs viewer)

- https://github.com/boz/kail

```shell
# tail-ит логи контейнеров всех подов на такой ноде
kail --node ip-10-10-38-223.us-east-1b.compute.internal
# tail-ит логи попавшие в матчер
kail -l app.kubernetes.io/name=traefik
```

[![asciicast](https://asciinema.org/a/133521.png)](https://asciinema.org/a/133521)

| --- | --- |
| `-l, --label LABEL-SELECTOR` | match pods based on a [standard label selector](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) |
| `-p, --pod NAME` | match pods by name |
| `-n, --ns NAMESPACE-NAME` | match pods in the given namespace |
| `--svc NAME` | match pods belonging to the given service |
| `--rc NAME` | match pods belonging to the given replication controller |
| `--rs NAME` | match pods belonging to the given replica set |
| `-d, --deploy NAME` | match pods belonging to the given deployment |
| `--sts NAME` | match pods belonging to the given statefulset |
| `-j, --job NAME` | match pods belonging to the given job |
| `--node NODE-NAME` | match pods running on the given node |
| `--ing NAME` | match pods belonging to services targeted by the given ingress |
| `-c, --containers CONTAINER-NAME` | restrict which containers logs are shown for |
| `--ignore LABEL-SELECTOR` | Ignore pods that the selector matches. (default: `kail.ignore=true`) |
| `--current-ns` | Match pods in the namespace specified in Kubernetes' "current context" |
| `--ignore-ns NAME` | Ignore pods in the given namespaces.  Overridden by `--ns`, `--current-ns`. (default: `kube-system`) |
