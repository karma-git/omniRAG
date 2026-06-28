---
title: "7 - Disable Root Login"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

After doing some security audits of servers, xFusionCorp Industries security team has implemented some new security policies. One of them is to disable direct root login through SSH.

Disable direct SSH root login on all app servers in Stratos Datacenter.

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
[root@stapp01 ~]# sed -i "s/#PermitRootLogin yes/PermitRootLogin no/g" /etc/ssh/sshd_config
[root@stapp01 ~]# systemctl restart sshd
```
