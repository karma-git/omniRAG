---
title: "3 - Create a Linux User with non-interactive shell"
tags:
  - kodekloud-engineer-sysadmin
---

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
[root@stapp01 ~]# adduser backup -s /sbin/nologin/
[root@stapp01 ~]# id backup; cat /etc/passwd | grep backup
```
