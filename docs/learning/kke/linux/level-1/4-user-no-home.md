---
title: "4 - Linux User Without Home"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The system admins team of xFusionCorp Industries has set up a new tool on all app servers, as they have a requirement to create a service user account that will be used by that tool. They are finished with all apps except for App Server 1 in Stratos Datacenter.

Create a user named javed in App Server 1 without a home directory

Look into the issue and fix the same.

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
[root@stapp01 ~]# useradd --no-create-home yousuf
[root@stapp01 ~]# cat /etc/passwd | grep yousuf
yousuf:x:1002:1002::/home/yousuf:/bin/bash
```
