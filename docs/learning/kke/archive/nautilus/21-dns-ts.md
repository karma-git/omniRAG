---
title: "21 - DNS Troubleshooting"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The system admins team of xFusionCorp Industries has noticed intermittent issues with DNS resolution in several apps . App Server 3 in Stratos Datacenter is having some DNS resolution issues, so we want to add some additional DNS nameservers on this server.

As a temporary fix we have decided to go with Google public DNS (ipv4). Please make appropriate changes on this server.


## Solution

```shell
thor@jump_host ~$ ssh banner@stapp03
[banner@stapp03 ~]$ sudo -i
[root@stapp03 ~]# cat /etc/resolv.conf
search stratos.xfusioncorp.com
nameserver 127.0.0.11
options ndots:0
[root@stapp03 ~]# vi /etc/resolv.conf
# NOTE add line -> nameserver: 8.8.8.8
```
