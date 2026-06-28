---
title: "17 - Linux Firewalld Rules"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The Nautilus system admins team recently deployed a web UI application for their backup utility running on the Nautilus backup server in Stratos Datacenter. The application is running on port 6000. They have firewalld installed on that server. The requirements that have come up include the following:

Open all incoming connection on 6000/tcp port. Zone should be public.

## Solution

```shell
thor@jump_host ~$ ssh clint@stbkp01
[clint@stbkp01 ~]$ sudo -i
[root@stbkp01 ~]# firewall-cmd --permanent --zone=public --add-port=6000/tcp
success
[root@stbkp01 ~]# firewall-cmd --reload
success
```
